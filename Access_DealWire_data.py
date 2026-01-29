import requests
import pandas as pd
from datetime import datetime

API_KEY = "dw_api_2026_xK9mPqR7vL3nWzY5tBcF8hJgNsQe"
API_ENDPOINT = "https://qqapyqjvnunsdzpbuikg.supabase.co/functions/v1/api-deals"

def fetch_deals(limit=100, offset=0):
    headers = {"x-api-key": API_KEY}
    params = {"limit": limit, "offset": offset}
    r = requests.get(API_ENDPOINT, headers=headers, params=params, timeout=60)
    r.raise_for_status()
    return r.json()

def fetch_all(page_size=500):
    all_rows = []
    offset = 0
    total = None

    while True:
        payload = fetch_deals(limit=page_size, offset=offset)
        batch = payload.get("data", [])
        if total is None:
            total = payload.get("total")

        if not batch:
            break

        all_rows.extend(batch)
        offset += len(batch)
        print(f"Fetched {len(batch)} (total fetched: {len(all_rows)} / {total if total is not None else '?'})")

        if total is not None and len(all_rows) >= total:
            break

    return all_rows

def main():
    deals = fetch_all(page_size=500)
    print(f"\nTotal deals fetched: {len(deals)}\n")

    # Print all deals
    for d in deals:
        print(f"{d.get('company','')} - {d.get('amount','')} ({d.get('stage','')}) | {d.get('location','')}")

    # Save to Excel
    df = pd.DataFrame(deals)

    # Order columns if present
    preferred = ["company", "amount", "stage", "location", "focus", "investors", "timestamp"]
    cols = [c for c in preferred if c in df.columns] + [c for c in df.columns if c not in preferred]
    df = df[cols]

    out = f"dealwire_deals_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    df.to_excel(out, index=False)
    print(f"\nSaved: {out}")

if __name__ == "__main__":
    main()
