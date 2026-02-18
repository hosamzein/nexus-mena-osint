from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from hashlib import sha1
from typing import List

from .schemas import (
    AlertRecord,
    AlertStatus,
    AnalysisResult,
    CaseReport,
    ContentItem,
    EvidenceRecord,
    MediaVerificationResult,
    Severity,
    VerificationVerdict,
)


def build_alerts(case_id: str, analysis: AnalysisResult) -> List[AlertRecord]:
    alerts: List[AlertRecord] = []
    now = datetime.now(timezone.utc)

    base_title = "Coordinated disinformation risk"
    recommendation = "Prioritize analyst validation, preserve evidence, and monitor spread velocity."
    alerts.append(
        AlertRecord(
            id=f"alert_{sha1((case_id + 'primary').encode()).hexdigest()[:10]}",
            case_id=case_id,
            severity=analysis.severity,
            status=AlertStatus.open,
            title=base_title,
            summary=f"Score {analysis.score} with top clusters: {', '.join(list(analysis.narrative_clusters.keys())[:3]) or 'none' }.",
            recommended_action=recommendation,
            created_at=now,
        )
    )

    if analysis.signals.cross_platform >= 40:
        alerts.append(
            AlertRecord(
                id=f"alert_{sha1((case_id + 'cross').encode()).hexdigest()[:10]}",
                case_id=case_id,
                severity=Severity.r3 if analysis.severity == Severity.r4 else analysis.severity,
                status=AlertStatus.open,
                title="Cross-platform amplification",
                summary="Narrative appears on multiple platforms and languages.",
                recommended_action="Escalate to campaign timeline review and monitor bridge accounts.",
                created_at=now,
            )
        )

    return alerts


def build_evidence(case_id: str, items: List[ContentItem]) -> List[EvidenceRecord]:
    evidence: List[EvidenceRecord] = []
    for item in items:
        evidence.append(
            EvidenceRecord(
                id=f"ev_{sha1((item.id + 'evidence').encode()).hexdigest()[:12]}",
                case_id=case_id,
                item_id=item.id,
                source_name=item.source_name,
                source_url=item.url,
                evidence_hash=sha1((item.text + item.url).encode()).hexdigest(),
                note="Captured by unified connector pipeline.",
                captured_at=datetime.now(timezone.utc),
            )
        )
    return evidence


def verify_media(items: List[ContentItem]) -> List[MediaVerificationResult]:
    hash_counter = Counter(item.media_hash for item in items if item.media_hash)
    results: List[MediaVerificationResult] = []
    for item in items:
        if not item.media_hash:
            continue
        reused = hash_counter[item.media_hash] > 1
        text_lower = item.text.lower()
        suspicious_caption = "unverifiable" in text_lower or "without" in text_lower
        checks = {
            "hash_reused": reused,
            "suspicious_caption": suspicious_caption,
            "source_consistent": item.source_name.startswith(item.platform.value),
        }
        if reused:
            verdict = VerificationVerdict.reused
            confidence = 0.87
            explanation = "Media hash appears in multiple posts, indicating potential recycling."
        elif suspicious_caption:
            verdict = VerificationVerdict.suspicious
            confidence = 0.74
            explanation = "Caption has unverifiable framing language."
        else:
            verdict = VerificationVerdict.likely_authentic
            confidence = 0.62
            explanation = "No immediate duplication or caption anomalies detected."
        results.append(
            MediaVerificationResult(
                item_id=item.id,
                verdict=verdict,
                confidence=confidence,
                checks=checks,
                explanation=explanation,
            )
        )
    return results


def build_case_report(case_id: str, analysis: AnalysisResult, items: List[ContentItem]) -> CaseReport:
    top_platforms = Counter(item.platform.value for item in items).most_common(3)
    platform_summary = ", ".join(f"{name} ({count})" for name, count in top_platforms) or "none"
    clusters = ", ".join(list(analysis.narrative_clusters.keys())[:4]) or "none"
    recommendations = [
        "Escalate R3/R4 alerts to analyst queue with evidence lock.",
        "Track bridge accounts and recurring narrative keys for 24h.",
        "Run cross-language verification on Arabic-English claim pairs.",
    ]
    if analysis.signals.credibility_gap > 35:
        recommendations.insert(0, "Prioritize source credibility audit for top-linked domains.")

    return CaseReport(
        case_id=case_id,
        headline=f"{analysis.severity.value} disinformation posture for case {case_id}",
        executive_summary=[
            f"Overall risk score is {analysis.score} ({analysis.severity.value}).",
            f"Top narrative clusters: {clusters}.",
            f"Primary platform distribution: {platform_summary}.",
        ],
        findings=[
            f"Cross-platform signal: {analysis.signals.cross_platform:.1f}.",
            f"Coordination signal: {analysis.signals.coordination:.1f}.",
            f"Credibility gap signal: {analysis.signals.credibility_gap:.1f}.",
        ],
        recommendations=recommendations,
        generated_at=datetime.now(timezone.utc),
    )
