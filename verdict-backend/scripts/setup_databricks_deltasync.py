"""
Create verdict catalog, schema, and Delta source tables via SQL warehouse.
Then create DELTA_SYNC vector search indexes.
"""
import sys, time, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from dotenv import load_dotenv; load_dotenv()
from app.config import settings
import httpx

base = settings.DATABRICKS_HOST
token = settings.DATABRICKS_TOKEN
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
WAREHOUSE_ID = "5c4a821a7b1f67e1"


def run_sql(sql, wait=True):
    """Execute SQL via the Databricks SQL statement API."""
    with httpx.Client(timeout=60) as client:
        r = client.post(
            f"{base}/api/2.0/sql/statements",
            headers=headers,
            json={
                "statement": sql,
                "warehouse_id": WAREHOUSE_ID,
                "wait_timeout": "30s",
                "on_wait_timeout": "CONTINUE",
            },
        )
        data = r.json()
        stmt_id = data.get("statement_id")
        status = data.get("status", {}).get("state", "UNKNOWN")

        if status in ("SUCCEEDED", "FAILED", "CANCELED", "CLOSED"):
            return status, data.get("status", {}).get("error", {}).get("message", "")

        # Poll for completion
        if wait and stmt_id:
            for _ in range(30):
                time.sleep(2)
                poll = client.get(f"{base}/api/2.0/sql/statements/{stmt_id}", headers=headers)
                pdata = poll.json()
                pstate = pdata.get("status", {}).get("state", "UNKNOWN")
                if pstate in ("SUCCEEDED", "FAILED", "CANCELED"):
                    return pstate, pdata.get("status", {}).get("error", {}).get("message", "")

        return status, ""


def create_catalog_and_schema():
    print("\n📦 Creating verdict catalog and schema...")
    sql_steps = [
        ("CREATE CATALOG", "CREATE CATALOG IF NOT EXISTS verdict"),
        ("CREATE SCHEMA", "CREATE SCHEMA IF NOT EXISTS verdict.sessions"),
    ]
    for name, sql in sql_steps:
        status, err = run_sql(sql)
        if status == "SUCCEEDED":
            print(f"   ✅ {name}")
        else:
            print(f"   ⚠️  {name}: {status} — {err}")


def create_source_tables():
    print("\n📋 Creating source Delta tables for vector indexes...")

    fre_table_sql = """
    CREATE TABLE IF NOT EXISTS verdict.sessions.fre_rules_source (
        id STRING NOT NULL,
        rule_number STRING,
        rule_title STRING,
        article STRING,
        category STRING,
        is_deposition_relevant STRING,
        chunk_type STRING,
        content STRING,
        doc_type STRING,
        source STRING
    )
    USING DELTA
    TBLPROPERTIES ('delta.enableChangeDataFeed' = 'true')
    """

    prior_table_sql = """
    CREATE TABLE IF NOT EXISTS verdict.sessions.prior_statements_source (
        id STRING NOT NULL,
        case_id STRING,
        document_id STRING,
        content STRING,
        page INT,
        line INT,
        doc_type STRING,
        witness_name STRING
    )
    USING DELTA
    TBLPROPERTIES ('delta.enableChangeDataFeed' = 'true')
    """

    for name, sql in [("fre_rules_source", fre_table_sql), ("prior_statements_source", prior_table_sql)]:
        status, err = run_sql(sql)
        if status == "SUCCEEDED":
            print(f"   ✅ {name} table created")
        else:
            print(f"   ⚠️  {name}: {status} — {err}")


def create_vector_indexes():
    from databricks.vector_search.client import VectorSearchClient
    print("\n🔍 Creating DELTA_SYNC vector indexes...")

    client = VectorSearchClient(
        workspace_url=base,
        personal_access_token=token,
        disable_notice=True,
    )

    endpoint = settings.DATABRICKS_VECTOR_ENDPOINT

    # FRE rules index
    try:
        client.create_delta_sync_index(
            endpoint_name=endpoint,
            index_name=settings.DATABRICKS_FRE_INDEX,
            primary_key="id",
            source_table_name="verdict.sessions.fre_rules_source",
            pipeline_type="TRIGGERED",
            embedding_source_column="content",
            embedding_model_endpoint_name="databricks-gte-large-en",
        )
        print("   ✅ FRE rules index created (DELTA_SYNC, auto-embedding)")
    except Exception as e:
        print(f"   ⚠️  FRE index: {e}")

    # Prior statements index
    try:
        client.create_delta_sync_index(
            endpoint_name=endpoint,
            index_name=settings.DATABRICKS_VECTOR_INDEX,
            primary_key="id",
            source_table_name="verdict.sessions.prior_statements_source",
            pipeline_type="TRIGGERED",
            embedding_source_column="content",
            embedding_model_endpoint_name="databricks-gte-large-en",
        )
        print("   ✅ Prior statements index created (DELTA_SYNC, auto-embedding)")
    except Exception as e:
        print(f"   ⚠️  Prior statements index: {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("VERDICT — Databricks DELTA_SYNC Setup")
    print("=" * 60)
    create_catalog_and_schema()
    create_source_tables()
    create_vector_indexes()
    print("\n✅ Setup complete! Run fre_ingest_sql.py next to load FRE corpus.")
