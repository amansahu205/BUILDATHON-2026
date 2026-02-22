"""Verify Databricks Vector Search indexes and ingest FRE corpus via DELTA_SYNC (SQL INSERT)."""
import sys, time, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from dotenv import load_dotenv; load_dotenv()
from app.config import settings
from databricks.vector_search.client import VectorSearchClient
import httpx

base = settings.DATABRICKS_HOST
token = settings.DATABRICKS_TOKEN
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
WAREHOUSE_ID = "5c4a821a7b1f67e1"

# ── FRE Rules ────────────────────────────────────────────────────────────────
FRE_RULES = [
    ("FRE 611(c)", "Mode and Order — Leading Questions", "VI", "LEADING",
     "FRE 611(c) — Leading Questions: Leading questions should not be used on direct examination except as necessary to develop the witness's testimony. Ordinarily, the court should allow leading questions on cross-examination. Questions beginning with Isn't it true that, Wouldn't you agree, or You knew, didn't you are prototypical leading questions objectionable under 611(c)."),
    ("FRE 801", "Definitions — Hearsay", "VIII", "HEARSAY",
     "FRE 801 — Hearsay: Hearsay means a statement that the declarant does not make while testifying at the current trial or hearing and a party offers to prove the truth of the matter asserted. Questions asking what another person said, told, wrote, or communicated call for hearsay. Questions like What did the doctor tell you? or What did your supervisor say? typically elicit hearsay."),
    ("FRE 802", "The Rule Against Hearsay", "VIII", "HEARSAY",
     "FRE 802 — The Rule Against Hearsay: Hearsay is not admissible unless a federal statute, the Federal Rules of Evidence, or other rules prescribed by the Supreme Court provide otherwise. At deposition, hearsay objections are preserved for trial; testimony is still taken subject to the objection."),
    ("FRE 803", "Exceptions to the Rule Against Hearsay", "VIII", "HEARSAY",
     "FRE 803 — Exceptions to Hearsay: Key exceptions include Present Sense Impression, Excited Utterance, Statements for Medical Diagnosis, and Business Records Rule 803(6). Medical records and business records are frequently invoked at depositions in personal injury and malpractice cases."),
    ("FRE 611(a)", "Mode and Order — Control by Court", "VI", "FORM",
     "FRE 611(a) — Control by the Court: The court should exercise reasonable control to make procedures effective, avoid wasting time, and protect witnesses from harassment. Compound questions combining two or more questions violate orderly examination and should be objected to as compound or confusing and misleading."),
    ("FRE 602", "Need for Personal Knowledge", "VI", "SPECULATION",
     "FRE 602 — Personal Knowledge: A witness may testify only if evidence is introduced sufficient to support a finding that the witness has personal knowledge. Questions calling for speculation include What do you think would have happened if, Isn't it possible that, and Why do you suppose. These elicit guesswork rather than direct knowledge."),
    ("FRE 403", "Excluding Relevant Evidence", "IV", "PREJUDICE",
     "FRE 403 — Excluding Relevant Evidence: The court may exclude relevant evidence if its probative value is substantially outweighed by unfair prejudice, confusing the issues, or misleading the jury. At deposition, harassing or embarrassing questions designed to intimidate rather than elicit relevant testimony may be objected to under FRE 403."),
    ("FRE 613", "Witness Prior Statement", "VI", "IMPEACHMENT",
     "FRE 613 — Prior Statements: When examining a witness about a prior statement, a party need not show it initially but must disclose it to adverse counsel on request. Extrinsic evidence of a prior inconsistent statement is admissible only if the witness is given an opportunity to explain. Prior deposition transcripts, sworn affidavits, and police reports may all be used to impeach under FRE 613."),
    ("FRE 701", "Opinion Testimony by Lay Witnesses", "VII", "SPECULATION",
     "FRE 701 — Lay Opinion: Lay witness testimony in opinion form is limited to opinions rationally based on the witness's perception, helpful to understanding the testimony, and not requiring specialized knowledge. Lay witnesses cannot offer opinions on medical causation, legal conclusions, or technical standards without direct perceptual basis."),
    ("FRE 611(b)", "Scope of Cross-Examination", "VI", "SCOPE",
     "FRE 611(b) — Scope of Cross-Examination: Cross-examination should not go beyond the subject matter of direct examination and matters affecting credibility. Questions that assume facts not in evidence — Isn't it true that you knew about the report when the witness denies knowledge — are objectionable as assuming facts not in evidence."),
    ("FRE 404(b)", "Other Crimes Wrongs or Acts", "IV", "CHARACTER",
     "FRE 404(b) — Other Acts: Evidence of prior crimes or bad acts is not admissible to prove character or propensity. May be admissible for motive, opportunity, intent, preparation, plan, knowledge, or absence of mistake. Deposition questions about prior bad acts solely to attack character are objectionable under 404(b)."),
    ("FRE 501", "Privilege in General", "V", "PRIVILEGE",
     "FRE 501 — Privilege: Common law governs privilege claims. Attorney-client privilege and work product doctrine are the most common objections at deposition. Questions asking what the witness discussed with their attorney or requesting attorney mental impressions are objectionable as privileged."),
]


def run_sql(sql):
    with httpx.Client(timeout=60) as client:
        r = client.post(
            f"{base}/api/2.0/sql/statements",
            headers=headers,
            json={"statement": sql, "warehouse_id": WAREHOUSE_ID, "wait_timeout": "30s"},
        )
        data = r.json()
        state = data.get("status", {}).get("state", "UNKNOWN")
        err = data.get("status", {}).get("error", {}).get("message", "")
        return state, err


def verify_indexes():
    client = VectorSearchClient(workspace_url=base, personal_access_token=token, disable_notice=True)
    try:
        ep = client.get_endpoint(name=settings.DATABRICKS_VECTOR_ENDPOINT)
        state = ep.get("endpoint_status", {}).get("state", "?")
        num = ep.get("num_indexes", 0)
        print(f"\n✅ Endpoint: {settings.DATABRICKS_VECTOR_ENDPOINT} — {state} ({num} indexes)")
    except Exception as e:
        print(f"   Endpoint check failed: {e}")


def ingest_fre():
    print(f"\n📤 Inserting {len(FRE_RULES)} FRE rules into Delta table...")
    for rule in FRE_RULES:
        rule_num, rule_title, article, category, content = rule
        import hashlib
        rid = hashlib.md5(rule_num.encode()).hexdigest()[:16]
        # Escape single quotes
        content_escaped = content.replace("'", "''")
        rule_num_e = rule_num.replace("'", "''")
        rule_title_e = rule_title.replace("'", "''")
        sql = f"""
        INSERT INTO verdict.sessions.fre_rules_source (id, rule_number, rule_title, article, category, is_deposition_relevant, chunk_type, content, doc_type, source)
        VALUES ('{rid}', '{rule_num_e}', '{rule_title_e}', '{article}', '{category}', 'true', 'rule_text', '{content_escaped}', 'FRE', 'uscode.house.gov')
        """
        state, err = run_sql(sql)
        icon = "✅" if state == "SUCCEEDED" else "⚠️"
        print(f"   {icon} {rule_num} — {state}{' | ' + err if err else ''}")
    print("\n✅ FRE corpus inserted into source table.")
    print("   Run: sync the DELTA_SYNC index to pick up the data.")


def sync_indexes():
    client = VectorSearchClient(workspace_url=base, personal_access_token=token, disable_notice=True)
    for idx_name in [settings.DATABRICKS_FRE_INDEX, settings.DATABRICKS_VECTOR_INDEX]:
        try:
            client.get_index(
                endpoint_name=settings.DATABRICKS_VECTOR_ENDPOINT,
                index_name=idx_name,
            ).sync()
            print(f"   ✅ Sync triggered for {idx_name}")
        except Exception as e:
            print(f"   ⚠️  Sync {idx_name}: {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("VERDICT — FRE Ingestion + Index Verification")
    print("=" * 60)
    verify_indexes()
    ingest_fre()
    print("\n🔄 Triggering index sync...")
    sync_indexes()
    print("\n🎉 Done! Objection Copilot can now query FRE rules.")
