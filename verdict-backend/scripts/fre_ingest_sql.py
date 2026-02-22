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
import json
fre_rules_path = Path(__file__).parent.parent.parent / "data" / "fre_rules_extracted.json"
try:
    with open(fre_rules_path, "r", encoding="utf-8") as f:
        FRE_RULES_JSON = json.load(f)
except FileNotFoundError:
    print(f"⚠️  Could not find {fre_rules_path}. Please run the extraction script first.")
    sys.exit(1)

FRE_RULES = []
for r in FRE_RULES_JSON:
    num = r.get('rule_number', '')
    title = r.get('rule_title', '')
    content = f"FRE {num} — {title}: {r.get('content', '')}"
    
    # We don't have strictly categorized rules for all 69 rules in the JSON, 
    # but the vector index will use the content to retrieve them anyway.
    category = "GENERAL"
    # Derive article (e.g., Rule 801 belongs to Article VIII)
    article_str = num[0] if len(num) == 3 and num[0].isdigit() else "I"
    
    FRE_RULES.append((f"FRE {num}", title, article_str, category, content))


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
