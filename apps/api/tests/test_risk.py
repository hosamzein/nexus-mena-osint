from app.analysis import analyze_items
from app.connectors import collect_case_items
from app.schemas import Platform


def test_analysis_score_in_expected_range() -> None:
    items = collect_case_items(
        case_id="case_test",
        query="energy misinformation",
        platforms=[Platform.x, Platform.telegram, Platform.instagram],
    )
    analysis = analyze_items(items)
    assert 0 <= analysis.score <= 100
    assert analysis.severity.value in {"R1", "R2", "R3", "R4"}
    assert analysis.narrative_clusters
