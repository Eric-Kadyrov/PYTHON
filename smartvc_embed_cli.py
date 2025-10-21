# smartvc_embed_cli.py
# Minimal CLI to (1) embed investors/funds/companies using OpenAI
# and (2) run a demo hybrid similarity search.
#
# Usage:
#   export OPENAI_API_KEY=...
#   export DATABASE_URL=postgresql://user:pass@host:5432/dbname
#   python smartvc_embed_cli.py --entity investors --limit 500
#   python smartvc_embed_cli.py --query "AI for materials science seed investor in USA" --regions USA,Europe --topk 25
#
# Note: Requires: pip install openai psycopg2-binary numpy

import os, argparse, psycopg2, json
from typing import List
from openai import OpenAI

DIM = 3072  # change if you use a different embedding model
EMBED_MODEL = "text-embedding-3-large"

def get_conn():
    dsn = os.environ.get("DATABASE_URL")
    if not dsn:
        raise SystemExit("DATABASE_URL env var not set")
    return psycopg2.connect(dsn)

def embed_text(client: OpenAI, text: str) -> List[float]:
    if not text:
        text = ""
    r = client.embeddings.create(model=EMBED_MODEL, input=text)
    return r.data[0].embedding

def upsert_entities(entity: str, limit: int):
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    conn = get_conn(); conn.autocommit = True
    cur = conn.cursor()

    if entity == "investors":
        cur.execute("""
            SELECT id, COALESCE(thesis,'') || ' ' || COALESCE(org_name,'') || ' ' || COALESCE(geography,'')
            FROM investors
            WHERE embedding IS NULL
            ORDER BY created_at DESC
            LIMIT %s
        """, (limit,))
        rows = cur.fetchall()
        for _id, text in rows:
            vec = embed_text(client, text)
            cur.execute("UPDATE investors SET embedding = %s WHERE id = %s", (vec, _id))

    elif entity == "funds":
        cur.execute("""
            SELECT id, COALESCE(name,'') || ' ' || COALESCE(website,'') || ' ' || COALESCE(sector_focus,'') || ' ' || COALESCE(stage_focus,'')
            FROM funds
            WHERE embedding IS NULL
            ORDER BY created_at DESC
            LIMIT %s
        """, (limit,))
        rows = cur.fetchall()
        for _id, text in rows:
            vec = embed_text(client, text)
            cur.execute("UPDATE funds SET embedding = %s WHERE id = %s", (vec, _id))

    elif entity == "companies":
        cur.execute("""
            SELECT id, COALESCE(description,'') || ' ' || COALESCE(sector,'') || ' ' || COALESCE(sub_sector,'')
            FROM companies
            WHERE embedding IS NULL
            ORDER BY created_at DESC
            LIMIT %s
        """, (limit,))
        rows = cur.fetchall()
        for _id, text in rows:
            vec = embed_text(client, text)
            cur.execute("UPDATE companies SET embedding = %s WHERE id = %s", (vec, _id))
    else:
        raise SystemExit("Unknown entity. Use: investors | funds | companies")

    print(f"Embedded {len(rows)} {entity}.")

def query_investors(query_text: str, regions_csv: str = "", topk: int = 20):
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    qvec = embed_text(client, query_text)

    regions = [r.strip() for r in regions_csv.split(",") if r.strip()] if regions_csv else None

    conn = get_conn(); cur = conn.cursor()
    if regions:
        sql = """
            SELECT id, name, org_name, thesis,
                   1 - (embedding <=> %s) AS cosine_score
            FROM investors
            WHERE embedding IS NOT NULL
              AND geography = ANY(%s)
            ORDER BY embedding <=> %s
            LIMIT %s
        """
        cur.execute(sql, (qvec, regions, qvec, topk))
    else:
        sql = """
            SELECT id, name, org_name, thesis,
                   1 - (embedding <=> %s) AS cosine_score
            FROM investors
            WHERE embedding IS NOT NULL
            ORDER BY embedding <=> %s
            LIMIT %s
        """
        cur.execute(sql, (qvec, qvec, topk))

    rows = cur.fetchall()
    print(f"Top {len(rows)} investors:")
    for r in rows:
        _id, name, org, thesis, score = r
        print(f"- {name} ({org}) :: score={score:.4f}")
    conn.close()

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--entity", help="embed: investors|funds|companies")
    ap.add_argument("--limit", type=int, default=200)
    ap.add_argument("--query", help="natural-language investor query to embed and search")
    ap.add_argument("--regions", help="CSV of regions (e.g., 'USA,Europe')", default="")
    ap.add_argument("--topk", type=int, default=20)
    args = ap.parse_args()

    if args.entity:
        upsert_entities(args.entity, args.limit)
    if args.query:
        query_investors(args.query, args.regions, args.topk)
