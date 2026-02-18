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

    graph_resp = client.get(f"/api/v1/cases/{case_id}/graph")
    assert graph_resp.status_code == 200
    assert len(graph_resp.json()["nodes"]) > 0
