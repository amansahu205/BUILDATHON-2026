"""
scripts/setup_databricks.py
One-time setup: creates the Vector Search endpoint and both indexes.

Usage:
    cd verdict-backend
    python scripts/setup_databricks.py

Requires in .env:
    DATABRICKS_HOST=https://adb-<workspace-id>.<region>.azuredatabricks.net
    DATABRICKS_TOKEN=dapi...
    DATABRICKS_VECTOR_ENDPOINT=verdict-vector-endpoint
    DATABRICKS_FRE_INDEX=verdict.sessions.fre_rules_index
    DATABRICKS_VECTOR_INDEX=verdict.sessions.prior_statements_index

Runtime: ~15 min first time (endpoint provisioning).
"""

import sys
import time
from dotenv import load_dotenv

load_dotenv()

from app.config import settings  # noqa: E402


def check_config():
    if not settings.DATABRICKS_HOST or not settings.DATABRICKS_TOKEN:
        print("❌ DATABRICKS_HOST and DATABRICKS_TOKEN must be set in .env")
        print("   Get them from: Databricks workspace → User Settings → Developer → Access Tokens")
        sys.exit(1)
    print(f"✅ Databricks host: {settings.DATABRICKS_HOST}")


def create_endpoint(client):
    endpoint_name = settings.DATABRICKS_VECTOR_ENDPOINT
    print(f"\n📡 Creating Vector Search endpoint '{endpoint_name}'...")
    print("   This takes ~15 minutes the first time. Please wait...")

    try:
        existing = client.list_endpoints()
        names = [e.get("name") for e in existing.get("endpoints", [])]
        if endpoint_name in names:
            print(f"   ✅ Endpoint '{endpoint_name}' already exists — skipping creation")
            return
    except Exception:
        pass

    client.create_endpoint_and_wait(
        name=endpoint_name,
        endpoint_type="STANDARD",
    )
    print(f"   ✅ Endpoint '{endpoint_name}' is ONLINE")


def create_fre_index(client):
    index_name = settings.DATABRICKS_FRE_INDEX
    endpoint_name = settings.DATABRICKS_VECTOR_ENDPOINT
    print(f"\n📚 Creating FRE rules index '{index_name}'...")

    try:
        existing = client.list_indexes(endpoint_name)
        names = [i.get("name") for i in existing.get("vector_indexes", [])]
        if index_name in names:
            print(f"   ✅ Index '{index_name}' already exists — skipping")
            return
    except Exception:
        pass

    client.create_direct_access_index(
        endpoint_name=endpoint_name,
        index_name=index_name,
        primary_key="id",
        embedding_dimension=1024,
        embedding_vector_column="embedding",
        schema={
            "id": "string",
            "rule_number": "string",
            "rule_title": "string",
            "article": "string",
            "category": "string",
            "is_deposition_relevant": "string",   # "true"/"false" strings for filter compat
            "chunk_type": "string",
            "content": "string",
            "doc_type": "string",
            "source": "string",
            "embedding": "array<float>",
        },
    )
    print(f"   ✅ FRE rules index created")


def create_prior_statements_index(client):
    index_name = settings.DATABRICKS_VECTOR_INDEX
    endpoint_name = settings.DATABRICKS_VECTOR_ENDPOINT
    print(f"\n📝 Creating prior statements index '{index_name}'...")

    try:
        existing = client.list_indexes(endpoint_name)
        names = [i.get("name") for i in existing.get("vector_indexes", [])]
        if index_name in names:
            print(f"   ✅ Index '{index_name}' already exists — skipping")
            return
    except Exception:
        pass

    client.create_direct_access_index(
        endpoint_name=endpoint_name,
        index_name=index_name,
        primary_key="id",
        embedding_dimension=1024,
        embedding_vector_column="embedding",
        schema={
            "id": "string",
            "case_id": "string",
            "document_id": "string",
            "content": "string",
            "page": "int",
            "line": "int",
            "doc_type": "string",
            "witness_name": "string",
            "embedding": "array<float>",
        },
    )
    print(f"   ✅ Prior statements index created")


def verify_indexes(client):
    endpoint_name = settings.DATABRICKS_VECTOR_ENDPOINT
    print(f"\n🔍 Verifying indexes on endpoint '{endpoint_name}'...")

    try:
        result = client.list_indexes(endpoint_name)
        indexes = result.get("vector_indexes", [])
        for idx in indexes:
            name = idx.get("name")
            status = idx.get("status", {}).get("ready", False)
            print(f"   {'✅' if status else '⏳'} {name} — {'READY' if status else 'provisioning...'}")
        print(f"\n   Total indexes: {len(indexes)}")
    except Exception as e:
        print(f"   ⚠️  Could not list indexes: {e}")


def main():
    print("=" * 60)
    print("VERDICT — Databricks Vector Search Setup")
    print("=" * 60)

    check_config()

    try:
        from databricks.vector_search.client import VectorSearchClient
    except ImportError:
        print("❌ databricks-vectorsearch not installed. Run: pip install databricks-vectorsearch")
        sys.exit(1)

    client = VectorSearchClient(
        workspace_url=settings.DATABRICKS_HOST,
        personal_access_token=settings.DATABRICKS_TOKEN,
        disable_notice=True,
    )

    create_endpoint(client)
    create_fre_index(client)
    create_prior_statements_index(client)
    verify_indexes(client)

    print("\n" + "=" * 60)
    print("✅ Databricks setup complete!")
    print("Next step: python scripts/fre_xml_ingestion.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
