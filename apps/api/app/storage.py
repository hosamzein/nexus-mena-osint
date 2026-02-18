from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List

from .schemas import (
    AlertRecord,
    CaseRecord,
    CaseReport,
    ContentItem,
    EvidenceRecord,
    GlobalMetrics,
    MediaVerificationResult,
    Severity,
    Status,
    TimelineEvent,
)


class InMemoryStore:
    def __init__(self) -> None:
        self.cases: Dict[str, CaseRecord] = {}
        self.items: Dict[str, List[ContentItem]] = {}
        self.alerts: Dict[str, List[AlertRecord]] = {}
        self.evidence: Dict[str, List[EvidenceRecord]] = {}
        self.timeline: Dict[str, List[TimelineEvent]] = {}
        self.reports: Dict[str, CaseReport] = {}
        self.media_verifications: Dict[str, List[MediaVerificationResult]] = {}

    def _add_timeline_event(self, case_id: str, event_type: str, summary: str, metadata: Dict | None = None) -> None:
        events = self.timeline.setdefault(case_id, [])
        events.append(
            TimelineEvent(
                id=f"evt_{len(events) + 1}_{case_id[-4:]}",
                case_id=case_id,
                event_type=event_type,
                summary=summary,
                created_at=datetime.now(timezone.utc),
                metadata=metadata or {},
            )
        )

    def create_case(self, case: CaseRecord) -> CaseRecord:
        self.cases[case.id] = case
        self.items[case.id] = []
        self.alerts[case.id] = []
        self.evidence[case.id] = []
        self.timeline[case.id] = []
        self.media_verifications[case.id] = []
        self._add_timeline_event(case.id, "case_created", "Investigation case created.")
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
        self._add_timeline_event(
            case_id,
            "collection_completed",
            f"Collected {len(new_items)} new items.",
            {"item_count": len(new_items)},
        )
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
        self._add_timeline_event(
            case_id,
            "analysis_completed",
            f"Analysis completed with score {score:.2f} ({severity.value}).",
            {"score": score, "severity": severity.value},
        )
        return case

    def save_alerts(self, case_id: str, alerts: List[AlertRecord]) -> None:
        self.alerts[case_id] = alerts
        self._add_timeline_event(case_id, "alerts_generated", f"Generated {len(alerts)} alerts.")

    def get_alerts(self, case_id: str) -> List[AlertRecord]:
        return self.alerts.get(case_id, [])

    def save_evidence(self, case_id: str, evidence: List[EvidenceRecord]) -> None:
        self.evidence[case_id] = evidence
        self._add_timeline_event(case_id, "evidence_captured", f"Captured {len(evidence)} evidence records.")

    def get_evidence(self, case_id: str) -> List[EvidenceRecord]:
        return self.evidence.get(case_id, [])

    def save_media_verification(self, case_id: str, results: List[MediaVerificationResult]) -> None:
        self.media_verifications[case_id] = results
        self._add_timeline_event(
            case_id,
            "media_verified",
            f"Media verification completed for {len(results)} items.",
        )

    def get_media_verification(self, case_id: str) -> List[MediaVerificationResult]:
        return self.media_verifications.get(case_id, [])

    def save_report(self, case_id: str, report: CaseReport) -> None:
        self.reports[case_id] = report
        self._add_timeline_event(case_id, "report_generated", "Executive and technical report generated.")

    def get_report(self, case_id: str) -> CaseReport | None:
        return self.reports.get(case_id)

    def get_timeline(self, case_id: str) -> List[TimelineEvent]:
        return self.timeline.get(case_id, [])

    def get_global_metrics(self) -> GlobalMetrics:
        all_cases = list(self.cases.values())
        total_cases = len(all_cases)
        avg_risk = sum(case.risk_score for case in all_cases) / total_cases if total_cases else 0.0
        open_alerts = sum(len([a for a in alerts if a.status == "open"]) for alerts in self.alerts.values())
        high = len([case for case in all_cases if case.severity in {Severity.r3, Severity.r4}])
        return GlobalMetrics(
            total_cases=total_cases,
            open_alerts=open_alerts,
            avg_risk=round(avg_risk, 2),
            high_severity_cases=high,
        )


store = InMemoryStore()
