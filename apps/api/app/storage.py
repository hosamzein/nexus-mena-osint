from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List

from .schemas import CaseRecord, ContentItem, Severity, Status


class InMemoryStore:
    def __init__(self) -> None:
        self.cases: Dict[str, CaseRecord] = {}
        self.items: Dict[str, List[ContentItem]] = {}

    def create_case(self, case: CaseRecord) -> CaseRecord:
        self.cases[case.id] = case
        self.items[case.id] = []
        return case

    def list_cases(self) -> List[CaseRecord]:
        return sorted(self.cases.values(), key=lambda x: x.updated_at, reverse=True)

    def get_case(self, case_id: str) -> CaseRecord:
        return self.cases[case_id]

    def append_items(self, case_id: str, new_items: List[ContentItem]) -> CaseRecord:
        case = self.get_case(case_id)
        case.status = Status.collecting
        case.updated_at = datetime.now(timezone.utc)
        self.items[case_id].extend(new_items)
        case.item_count = len(self.items[case_id])
        return case

    def get_items(self, case_id: str) -> List[ContentItem]:
        return self.items.get(case_id, [])

    def save_analysis(self, case_id: str, score: float, severity: Severity, analysis) -> CaseRecord:
        case = self.get_case(case_id)
        case.status = Status.ready
        case.risk_score = score
        case.severity = severity
        case.analysis = analysis
        case.updated_at = datetime.now(timezone.utc)
        return case


store = InMemoryStore()
