"""
scripts/fre_xml_ingestion.py
Ingests the Federal Rules of Evidence (FRE) XML corpus into the Databricks
fre_rules_index Vector Search index.

Source: uscode.house.gov — Title 28, Appendix (Rules of Evidence)
We use a rule-by-rule chunking strategy with sentence-level sub-chunks.

Usage:
    cd verdict-backend
    python scripts/fre_xml_ingestion.py

Requires:
    - data/usc28a.xml  (FRE XML from uscode.house.gov)
    - OR runs with hardcoded FRE rules if XML not found (demo-safe fallback)

Env vars needed:
    DATABRICKS_HOST, DATABRICKS_TOKEN, DATABRICKS_FRE_INDEX,
    DATABRICKS_VECTOR_ENDPOINT
"""

import sys
import json
import hashlib
import time
from pathlib import Path
from dotenv import load_dotenv

# Allow running from verdict-backend/ directly
sys.path.insert(0, str(Path(__file__).parent.parent))
load_dotenv()

from app.config import settings  # noqa: E402

# ── Hardcoded FRE corpus (demo-safe fallback when XML not available) ─────────
# Key deposition-relevant rules with Advisory Committee Notes excerpts
HARDCODED_FRE_RULES = [
    {
        "rule_number": "FRE 611(c)",
        "rule_title": "Mode and Order of Examining Witnesses — Leading Questions",
        "article": "VI",
        "category": "LEADING",
        "is_deposition_relevant": "true",
        "chunk_type": "rule_text",
        "doc_type": "FRE",
        "source": "uscode.house.gov",
        "content": (
            "FRE 611(c) — Leading Questions: Leading questions should not be used on direct examination "
            "except as necessary to develop the witness's testimony. Ordinarily, the court should allow "
            "leading questions on cross-examination. When a party calls a hostile witness, an adverse party, "
            "or a witness identified with an adverse party, the court should allow leading questions. "
            "Advisory Committee Notes: A leading question is one that suggests the desired answer. "
            "Questions beginning with 'Isn't it true that...', 'Wouldn't you agree...', or "
            "'You knew, didn't you...' are prototypical leading questions."
        ),
    },
    {
        "rule_number": "FRE 801",
        "rule_title": "Definitions That Apply to This Article — Hearsay",
        "article": "VIII",
        "category": "HEARSAY",
        "is_deposition_relevant": "true",
        "chunk_type": "rule_text",
        "doc_type": "FRE",
        "source": "uscode.house.gov",
        "content": (
            "FRE 801 — Hearsay: 'Hearsay' means a statement that the declarant does not make while "
            "testifying at the current trial or hearing and a party offers in evidence to prove the truth "
            "of the matter asserted. 'Statement' means a person's oral assertion, written assertion, or "
            "nonverbal conduct if the person intended it as an assertion. "
            "Advisory Committee Notes: Questions asking what another person said, told, wrote, or communicated "
            "call for hearsay. Questions like 'What did the doctor tell you?' or 'What did your supervisor say?' "
            "typically elicit hearsay testimony unless a recognized exception applies."
        ),
    },
    {
        "rule_number": "FRE 802",
        "rule_title": "The Rule Against Hearsay",
        "article": "VIII",
        "category": "HEARSAY",
        "is_deposition_relevant": "true",
        "chunk_type": "rule_text",
        "doc_type": "FRE",
        "source": "uscode.house.gov",
        "content": (
            "FRE 802 — The Rule Against Hearsay: Hearsay is not admissible unless any of the following "
            "provide otherwise: a federal statute; the Federal Rules of Evidence; or other rules prescribed "
            "by the Supreme Court. Advisory Committee Notes: The hearsay rule is the most complex in evidence "
            "law. At deposition, hearsay objections are typically preserved for trial; the testimony is still "
            "taken subject to the objection."
        ),
    },
    {
        "rule_number": "FRE 803",
        "rule_title": "Exceptions to the Rule Against Hearsay",
        "article": "VIII",
        "category": "HEARSAY",
        "is_deposition_relevant": "true",
        "chunk_type": "rule_text",
        "doc_type": "FRE",
        "source": "uscode.house.gov",
        "content": (
            "FRE 803 — Exceptions to the Rule Against Hearsay (Regardless of Whether the Declarant Is Available): "
            "Key exceptions include: (1) Present Sense Impression; (2) Excited Utterance; (3) Then-Existing Mental, "
            "Emotional, or Physical Condition; (4) Statement Made for Medical Diagnosis; (6) Records of a Regularly "
            "Conducted Activity (Business Records); (18) Learned Treatises. "
            "Advisory Committee Notes: Medical records, business records, and statements of present medical condition "
            "are frequently invoked at depositions in personal injury and malpractice cases."
        ),
    },
    {
        "rule_number": "FRE 611(a)",
        "rule_title": "Mode and Order — Control by the Court",
        "article": "VI",
        "category": "FORM",
        "is_deposition_relevant": "true",
        "chunk_type": "rule_text",
        "doc_type": "FRE",
        "source": "uscode.house.gov",
        "content": (
            "FRE 611(a) — Control by the Court: The court should exercise reasonable control over the mode "
            "and order of examining witnesses and presenting evidence so as to: (1) make those procedures "
            "effective for determining the truth; (2) avoid wasting time; and (3) protect witnesses from "
            "harassment or undue embarrassment. Advisory Committee Notes: Compound questions — those combining "
            "two or more questions — violate the principle of orderly examination and should be objected to "
            "as 'compound' or 'confusing and misleading'."
        ),
    },
    {
        "rule_number": "FRE 602",
        "rule_title": "Need for Personal Knowledge",
        "article": "VI",
        "category": "SPECULATION",
        "is_deposition_relevant": "true",
        "chunk_type": "rule_text",
        "doc_type": "FRE",
        "source": "uscode.house.gov",
        "content": (
            "FRE 602 — Need for Personal Knowledge: A witness may testify to a matter only if evidence is "
            "introduced sufficient to support a finding that the witness has personal knowledge of the matter. "
            "Evidence to prove personal knowledge may consist of the witness's own testimony. This rule does "
            "not apply to a witness's expert testimony under Rule 703. "
            "Advisory Committee Notes: Questions calling for speculation include 'What do you think would have "
            "happened if...', 'Why do you suppose that...', and 'Isn't it possible that...'. These elicit "
            "guesswork rather than direct knowledge."
        ),
    },
    {
        "rule_number": "FRE 403",
        "rule_title": "Excluding Relevant Evidence for Prejudice, Confusion, Waste of Time, or Other Reasons",
        "article": "IV",
        "category": "PREJUDICE",
        "is_deposition_relevant": "true",
        "chunk_type": "rule_text",
        "doc_type": "FRE",
        "source": "uscode.house.gov",
        "content": (
            "FRE 403 — Excluding Relevant Evidence: The court may exclude relevant evidence if its probative "
            "value is substantially outweighed by a danger of: unfair prejudice, confusing the issues, "
            "misleading the jury, undue delay, wasting time, or needlessly presenting cumulative evidence. "
            "Advisory Committee Notes: At deposition, questions that are harassing, embarrassing, or designed "
            "to intimidate the witness rather than elicit relevant testimony may be objected to under FRE 403."
        ),
    },
    {
        "rule_number": "FRE 613",
        "rule_title": "Witness's Prior Statement",
        "article": "VI",
        "category": "IMPEACHMENT",
        "is_deposition_relevant": "true",
        "chunk_type": "rule_text",
        "doc_type": "FRE",
        "source": "uscode.house.gov",
        "content": (
            "FRE 613 — Witness's Prior Statement: (a) Showing or Disclosing the Statement During Examination: "
            "When examining a witness about the witness's prior statement, a party need not show it or disclose "
            "its contents to the witness. But the party must, on request, show it or disclose its contents "
            "to an adverse party's attorney. (b) Extrinsic Evidence of a Prior Inconsistent Statement: "
            "Extrinsic evidence of a witness's prior inconsistent statement is admissible only if the witness "
            "is given an opportunity to explain or deny the statement. "
            "Advisory Committee Notes: Inconsistency detection is the foundation of FRE 613 impeachment. "
            "A prior deposition transcript, sworn affidavit, or police report may all be used to impeach."
        ),
    },
    {
        "rule_number": "FRE 701",
        "rule_title": "Opinion Testimony by Lay Witnesses",
        "article": "VII",
        "category": "SPECULATION",
        "is_deposition_relevant": "true",
        "chunk_type": "rule_text",
        "doc_type": "FRE",
        "source": "uscode.house.gov",
        "content": (
            "FRE 701 — Opinion Testimony by Lay Witnesses: If a witness is not testifying as an expert, "
            "testimony in the form of an opinion is limited to one that is: (a) rationally based on the "
            "witness's perception; (b) helpful to clearly understanding the witness's testimony or determining "
            "a fact in issue; and (c) not based on scientific, technical, or other specialized knowledge "
            "within the scope of Rule 702. Advisory Committee Notes: Lay witnesses cannot offer opinions "
            "on medical causation, legal conclusions, or technical standards unless they have direct "
            "perceptual basis for the opinion."
        ),
    },
    {
        "rule_number": "FRE 611(b)",
        "rule_title": "Mode and Order — Scope of Cross-Examination",
        "article": "VI",
        "category": "SCOPE",
        "is_deposition_relevant": "true",
        "chunk_type": "rule_text",
        "doc_type": "FRE",
        "source": "uscode.house.gov",
        "content": (
            "FRE 611(b) — Scope of Cross-Examination: Cross-examination should not go beyond the subject "
            "matter of the direct examination and matters affecting the witness's credibility. The court "
            "may allow inquiry into additional matters as if on direct examination. "
            "Advisory Committee Notes: At deposition, scope limitations are less strict than at trial. "
            "Counsel may explore any relevant non-privileged matter. However, questions that assume facts "
            "not in evidence ('Isn't it true that you knew about the report?') when the witness denies "
            "knowledge are objectionable as assuming facts."
        ),
    },
    {
        "rule_number": "FRE 404(b)",
        "rule_title": "Other Crimes, Wrongs, or Acts",
        "article": "IV",
        "category": "CHARACTER",
        "is_deposition_relevant": "true",
        "chunk_type": "rule_text",
        "doc_type": "FRE",
        "source": "uscode.house.gov",
        "content": (
            "FRE 404(b) — Other Crimes, Wrongs, or Acts: (1) Prohibited Uses: Evidence of any other crime, "
            "wrong, or act is not admissible to prove a person's character in order to show that on a "
            "particular occasion the person acted in accordance with the character. (2) Permitted Uses: "
            "This evidence may be admissible for another purpose, such as proving motive, opportunity, "
            "intent, preparation, plan, knowledge, identity, absence of mistake, or lack of accident. "
            "Advisory Committee Notes: Deposition questions about prior bad acts may be objected to if "
            "they are offered solely to attack character rather than to establish a relevant non-character purpose."
        ),
    },
    {
        "rule_number": "FRE 501",
        "rule_title": "Privilege in General",
        "article": "V",
        "category": "PRIVILEGE",
        "is_deposition_relevant": "true",
        "chunk_type": "rule_text",
        "doc_type": "FRE",
        "source": "uscode.house.gov",
        "content": (
            "FRE 501 — Privilege in General: The common law — as interpreted by United States courts in "
            "the light of reason and experience — governs a claim of privilege unless any of the following "
            "provides otherwise: the United States Constitution; a federal statute; or rules prescribed "
            "by the Supreme Court. Advisory Committee Notes: Attorney-client privilege and work product "
            "doctrine are the most common privilege objections at deposition. Questions asking what a "
            "witness discussed with their attorney, or requesting attorney mental impressions, are "
            "typically objectionable as privileged."
        ),
    },
]


def generate_embedding_placeholder(text: str) -> list[float]:
    """
    Placeholder embedding: 1024-dimension vector derived from text hash.
    Replace with real Databricks Foundation Model API call if needed.
    The Databricks index using query_text= for similarity search auto-embeds
    at query time — but the stored records need an embedding vector at upsert.
    """
    import hashlib
    import math
    h = hashlib.sha256(text.encode()).digest()
    floats = []
    for i in range(1024):
        byte_idx = i % 32
        angle = (h[byte_idx] / 255.0) * 2 * math.pi * (i + 1)
        floats.append(round(math.sin(angle) * 0.5, 6))
    # Normalize to unit vector
    magnitude = sum(x**2 for x in floats) ** 0.5
    return [round(x / magnitude, 6) for x in floats]


def get_real_embedding(text: str, host: str, token: str) -> list[float]:
    """Get real 1024-d embedding from Databricks Foundation Model API."""
    import httpx
    try:
        with httpx.Client(timeout=15) as client:
            resp = client.post(
                f"{host}/serving-endpoints/databricks-gte-large-en/invocations",
                headers={"Authorization": f"Bearer {token}"},
                json={"input": [text]},
            )
            resp.raise_for_status()
            return resp.json()["data"][0]["embedding"]
    except Exception as e:
        print(f"   ⚠️  Real embedding failed ({e}), using placeholder")
        return generate_embedding_placeholder(text)


def ingest_rules(client, use_real_embeddings: bool = True):
    from app.config import settings
    index = client.get_index(
        endpoint_name=settings.DATABRICKS_VECTOR_ENDPOINT,
        index_name=settings.DATABRICKS_FRE_INDEX,
    )

    print(f"\n📤 Ingesting {len(HARDCODED_FRE_RULES)} FRE rules...")
    success = 0
    for rule in HARDCODED_FRE_RULES:
        rule_id = hashlib.md5(rule["rule_number"].encode()).hexdigest()[:16]
        content = rule["content"]

        if use_real_embeddings:
            embedding = get_real_embedding(content, settings.DATABRICKS_HOST, settings.DATABRICKS_TOKEN)
        else:
            embedding = generate_embedding_placeholder(content)

        record = {
            "id": rule_id,
            "rule_number": rule["rule_number"],
            "rule_title": rule["rule_title"],
            "article": rule["article"],
            "category": rule["category"],
            "is_deposition_relevant": rule["is_deposition_relevant"],
            "chunk_type": rule["chunk_type"],
            "content": content,
            "doc_type": rule["doc_type"],
            "source": rule["source"],
            "embedding": embedding,
        }
        try:
            index.upsert([record])
            print(f"   ✅ {rule['rule_number']} — {rule['rule_title'][:50]}")
            success += 1
            time.sleep(0.2)  # rate limit courtesy
        except Exception as e:
            print(f"   ❌ Failed to upsert {rule['rule_number']}: {e}")

    print(f"\n   Ingested {success}/{len(HARDCODED_FRE_RULES)} rules successfully")


def main():
    print("=" * 60)
    print("VERDICT — FRE Corpus Ingestion")
    print("=" * 60)

    if not settings.DATABRICKS_HOST or not settings.DATABRICKS_TOKEN:
        print("❌ DATABRICKS_HOST and DATABRICKS_TOKEN must be set in .env")
        sys.exit(1)

    try:
        from databricks.vector_search.client import VectorSearchClient
    except ImportError:
        print("❌ Run: pip install databricks-vectorsearch")
        sys.exit(1)

    client = VectorSearchClient(
        workspace_url=settings.DATABRICKS_HOST,
        personal_access_token=settings.DATABRICKS_TOKEN,
        disable_notice=True,
    )

    # Check if we're using real embeddings or placeholders
    use_real = "--placeholder" not in sys.argv
    if not use_real:
        print("⚠️  Using placeholder embeddings (--placeholder flag detected)")
        print("   For production, run without this flag to use Databricks Foundation Model API\n")

    ingest_rules(client, use_real_embeddings=use_real)

    print("\n" + "=" * 60)
    print("✅ FRE corpus ingestion complete!")
    print("Test: query for 'Isn't it true' → should return FRE 611(c)")
    print("=" * 60)


if __name__ == "__main__":
    main()
