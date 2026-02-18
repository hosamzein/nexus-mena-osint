from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from statistics import mean
from typing import Dict, List

from .schemas import AnalysisResult, ContentItem, RiskSignals, Severity


def _clamp(value: float) -> float:
    return max(0.0, min(100.0, value))


def _cluster_narratives(items: List[ContentItem]) -> Dict[str, int]:
    clusters: Counter[str] = Counter()
    for item in items:
        text = item.text.lower()
        if "coordinated" in text or "synchronize" in text:
            clusters["coordinated-amplification"] += 1
        if "unverifiable" in text or "no cited source" in text:
            clusters["source-credibility-gap"] += 1
        if "reused" in text or "re-uploaded" in text or "recycled" in text:
            clusters["media-recontextualization"] += 1
        if "claims" in text:
            clusters["claims-propagation"] += 1
    return dict(clusters)


def _signals(items: List[ContentItem]) -> RiskSignals:
    if not items:
        return RiskSignals()

    engagement_values = [item.engagement for item in items]
    avg_engagement = mean(engagement_values)
    platform_count = len(set(item.platform for item in items))
    language_count = len(set(item.language for item in items))
    authors = [item.author for item in items]
    duplicate_authors = len(authors) - len(set(authors))

    harm = _clamp(35 + (8 if any("casualty" in item.text.lower() for item in items) else 0))
    velocity = _clamp(20 + (len(items) * 2.2))
    reach = _clamp(avg_engagement / 6.0)
    coordination = _clamp(18 + duplicate_authors * 4 + (10 if len(items) > 14 else 0))
    credibility_gap = _clamp(25 + (12 if any("unverifiable" in item.text.lower() for item in items) else 0))
    cross_platform = _clamp(platform_count * 15 + language_count * 8)

    return RiskSignals(
        harm=harm,
        velocity=velocity,
        reach=reach,
        coordination=coordination,
        credibility_gap=credibility_gap,
        cross_platform=cross_platform,
    )


def _score_from_signals(signals: RiskSignals) -> float:
    return _clamp(
        signals.harm * 0.25
        + signals.coordination * 0.2
        + signals.velocity * 0.2
        + signals.reach * 0.15
        + signals.cross_platform * 0.1
        + signals.credibility_gap * 0.1
    )


def _severity(score: float) -> Severity:
    if score >= 75:
        return Severity.r4
    if score >= 55:
        return Severity.r3
    if score >= 30:
        return Severity.r2
    return Severity.r1


def analyze_items(items: List[ContentItem]) -> AnalysisResult:
    signals = _signals(items)
    score = _score_from_signals(signals)
    clusters = _cluster_narratives(items)
    entity_counter: Counter[str] = Counter()
    account_counter: Counter[str] = Counter()
    language_counter: Counter[str] = Counter()
    for item in items:
        entity_counter.update(item.entities)
        account_counter.update([item.author])
        language_counter.update([item.language])

    return AnalysisResult(
        signals=signals,
        score=round(score, 2),
        severity=_severity(score),
        narrative_clusters=clusters,
        top_entities=[name for name, _ in entity_counter.most_common(6)],
        top_accounts=[name for name, _ in account_counter.most_common(5)],
        language_distribution=dict(language_counter),
        generated_at=datetime.now(timezone.utc),
    )
