import os
import json
import sys
from typing import List, Dict

import requests

# List of customer request IDs to check. Duplicate IDs are automatically filtered out.
REQUEST_IDS: List[str] = [
    "bc-53e6b4fb-f99d-4529-8009-87cded370c2e",
    "bc-6f51d46b-acaf-4420-bfcc-dde383262ffd",
    "bc-cd787b2b-846c-408f-af2e-8a5e6dcb7034",
    "bc-d53b7194-4c63-47f4-bbec-9c3d1733c0da",
    "bc-66385910-81dd-4a15-a5c2-898ca178f28f",
    "bc-2a36493e-cecb-41f8-9649-fbaa8065651b",
    "bc-36b47a15-eb80-4e9d-b43a-92a03d37dd68",
    "bc-b8a7ba53-02bb-4085-8b00-f48ba8692c72",
    "bc-f2de85d5-4b15-44df-b29e-67063e1ee43e",
    "bc-d9db207a-9c0f-4c8f-9d0e-6765fb09fe17",
    "bc-c6862013-0867-4580-a63e-ec3dcfe80612",
    "bc-769fce79-ac2e-47ac-9b4b-dcd441c51f57",
    "bc-ac204b85-e66f-47bd-b94f-5a72258e758b",
    "bc-757ca27c-5f17-4639-be3a-c40db5ad84cb",
    "bc-29647012-64a3-410a-8551-5829d66c5c2f",
    "bc-379f5c75-324c-4808-8f15-327c28a7bb01",
    "bc-21237909-c807-4d00-8870-ed90dca01651",
    "bc-3705fce2-ce8c-467c-b7e7-05c19f29128e",
    "bc-a271ece5-14e1-40bf-b45a-226ad6a6aa80",
    "bc-84e08487-7dec-4dfb-9eec-3c224e2b8424",
]

# Configuration
# Set API_BASE_URL and, optionally, API_TOKEN via environment variables or edit defaults below.
API_BASE_URL: str = os.getenv("API_BASE_URL", "https://api.example.com")
API_TOKEN: str | None = os.getenv("API_TOKEN")

# Endpoint template where {request_id} will be replaced by the actual ID.
ENDPOINT_TEMPLATE: str = os.getenv("STATUS_ENDPOINT_TEMPLATE", "/customer/status/{request_id}")

def build_url(request_id: str) -> str:
    """Construct the full request URL for a given ID."""
    if "{request_id}" not in ENDPOINT_TEMPLATE:
        raise ValueError("STATUS_ENDPOINT_TEMPLATE must contain '{request_id}' placeholder")
    path = ENDPOINT_TEMPLATE.replace("{request_id}", request_id)
    return API_BASE_URL.rstrip("/") + path


def fetch_status(request_id: str) -> Dict[str, str] | str:
    """Fetch status for a single request ID. Returns parsed JSON or raw text."""
    url = build_url(request_id)
    headers: Dict[str, str] = {"Accept": "application/json"}
    if API_TOKEN:
        headers["Authorization"] = f"Bearer {API_TOKEN}"

    try:
        response = requests.get(url, headers=headers, timeout=15)
    except requests.exceptions.RequestException as exc:
        return {"error": str(exc)}

    if response.ok:
        # Try parsing JSON, fallback to raw text
        try:
            return response.json()
        except json.JSONDecodeError:
            return {"status": response.text.strip()}
    else:
        return {"http_status": response.status_code, "body": response.text.strip()}


def main() -> None:
    unique_ids = sorted(set(REQUEST_IDS))
    print(f"Checking status for {len(unique_ids)} unique request IDs...\n")
    for rid in unique_ids:
        result = fetch_status(rid)
        print(f"{rid}: {result}")


if __name__ == "__main__":
    main()