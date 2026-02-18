from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_case_flow() -> None:
    create_resp = client.post(
        "/api/v1/cases",
        json={
            "title": "Campaign pulse for regional topic",
            "query": "regional narrative wave",
            "platforms": ["x", "telegram", "youtube", "instagram", "web"],
        },
    )
    assert create_resp.status_code == 200
    case_id = create_resp.json()["id"]

    collect_resp = client.post(f"/api/v1/cases/{case_id}/collect")
    assert collect_resp.status_code == 200
    assert collect_resp.json()["item_count"] > 0

    analyze_resp = client.post(f"/api/v1/cases/{case_id}/analyze")
    assert analyze_resp.status_code == 200
    assert analyze_resp.json()["analysis"] is not None
    assert analyze_resp.json()["item_count"] > 0

    graph_resp = client.get(f"/api/v1/cases/{case_id}/graph")
    assert graph_resp.status_code == 200
    assert len(graph_resp.json()["nodes"]) > 0

    items_resp = client.get(f"/api/v1/cases/{case_id}/items")
    assert items_resp.status_code == 200
    assert len(items_resp.json()) > 0

    alerts_resp = client.get(f"/api/v1/cases/{case_id}/alerts")
    assert alerts_resp.status_code == 200
    assert len(alerts_resp.json()) > 0

    evidence_resp = client.get(f"/api/v1/cases/{case_id}/evidence")
    assert evidence_resp.status_code == 200
    assert len(evidence_resp.json()) > 0

    timeline_resp = client.get(f"/api/v1/cases/{case_id}/timeline")
    assert timeline_resp.status_code == 200
    assert len(timeline_resp.json()) > 0

    report_resp = client.get(f"/api/v1/cases/{case_id}/report")
    assert report_resp.status_code == 200
    assert "executive_summary" in report_resp.json()

    media_resp = client.get(f"/api/v1/cases/{case_id}/media-verification")
    assert media_resp.status_code == 200


def test_global_catalog_and_connectors() -> None:
    metrics = client.get("/api/v1/metrics")
    assert metrics.status_code == 200
    assert "total_cases" in metrics.json()

    connectors = client.get("/api/v1/connectors")
    assert connectors.status_code == 200
    assert len(connectors.json()) > 0

    catalog = client.get("/api/v1/source-catalog")
    assert catalog.status_code == 200
    assert len(catalog.json()) > 0
