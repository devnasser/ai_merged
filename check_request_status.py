import os
import sys
import argparse
import json
from typing import List, Dict

import requests

API_BASE_URL_ENV = "REQUEST_STATUS_API_BASE_URL"
API_TOKEN_ENV = "REQUEST_STATUS_API_TOKEN"

def read_ids_from_stdin() -> List[str]:
    """Read whitespace-separated IDs from STDIN."""
    raw = sys.stdin.read()
    return [part.strip() for part in raw.split() if part.strip()]

def unique_preserve_order(seq: List[str]) -> List[str]:
    """Return a list with duplicates removed while preserving original order."""
    seen = set()
    unique_list = []
    for item in seq:
        if item not in seen:
            seen.add(item)
            unique_list.append(item)
    return unique_list

def fetch_status(request_id: str, session: requests.Session, base_url: str, token: str = None) -> Dict:
    """Fetch status for a single request ID.

    Returns a dictionary with at least {"id": request_id, "status": <str>}.
    If the request fails, status will be "UNKNOWN" and the error appended in "error" key.
    """
    url = f"{base_url.rstrip('/')}/{request_id}"
    headers = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        resp = session.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        status_val = data.get("status") or data.get("state") or "UNKNOWN"
        return {"id": request_id, "status": status_val, "raw": data}
    except Exception as exc:
        return {"id": request_id, "status": "UNKNOWN", "error": str(exc)}

def main():
    parser = argparse.ArgumentParser(description="Check operational status for a list of request IDs")
    parser.add_argument("--base-url", help=f"API base URL (can also be set via {API_BASE_URL_ENV})")
    parser.add_argument("--token", help=f"Auth token (can also be set via {API_TOKEN_ENV})")
    args = parser.parse_args()

    base_url = args.base_url or os.getenv(API_BASE_URL_ENV)
    token = args.token or os.getenv(API_TOKEN_ENV)

    if not base_url:
        print("Error: API base URL not provided. Use --base-url or set environment variable.", file=sys.stderr)
        sys.exit(1)

    ids = unique_preserve_order(read_ids_from_stdin())
    if not ids:
        print("No IDs provided on STDIN", file=sys.stderr)
        sys.exit(1)

    results = []
    session = requests.Session()
    for rid in ids:
        results.append(fetch_status(rid, session, base_url, token))

    # Print in a nice table
    print("ID,STATUS")
    for r in results:
        print(f"{r['id']},{r['status']}")

    # Optionally, write full details to JSON file
    details_file = os.getenv("REQUEST_STATUS_DETAILS_FILE")
    if details_file:
        with open(details_file, "w", encoding="utf-8") as fh:
            json.dump(results, fh, ensure_ascii=False, indent=2)
        print(f"Detailed results written to {details_file}")

if __name__ == "__main__":
    main()