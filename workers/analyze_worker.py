from __future__ import annotations

import os
import time

import httpx


API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
POLL_SECONDS = int(os.getenv("ANALYZE_POLL_SECONDS", "45"))


def run() -> None:
    while True:
        with httpx.Client(timeout=20) as client:
            cases = client.get(f"{API_BASE_URL}/api/v1/cases").json()
            for case in cases:
                if case["item_count"] > 0 and case["status"] != "ready":
                    client.post(f"{API_BASE_URL}/api/v1/cases/{case['id']}/analyze")
                    print(f"[analyze] analyzed case={case['id']}")
        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    run()
