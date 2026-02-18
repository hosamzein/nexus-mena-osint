# Workers

Background workers are designed for scheduled orchestration outside the web and API request lifecycle.

- `ingest_worker.py`: polls draft/active cases and triggers collection.
- `analyze_worker.py`: triggers analysis and updates risk posture.

Set `API_BASE_URL` before running.
