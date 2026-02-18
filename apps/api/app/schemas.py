from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class Platform(str, Enum):
    x = "x"
    telegram = "telegram"
    youtube = "youtube"
    instagram = "instagram"
    web = "web"


class Severity(str, Enum):
    r1 = "R1"
    r2 = "R2"
    r3 = "R3"
    r4 = "R4"


class Status(str, Enum):
    draft = "draft"
    collecting = "collecting"
    analyzing = "analyzing"
    ready = "ready"


class AlertStatus(str, Enum):
    open = "open"
    triaged = "triaged"
    closed = "closed"


class VerificationVerdict(str, Enum):
    likely_authentic = "likely_authentic"
    suspicious = "suspicious"
    reused = "reused"


class CreateCaseRequest(BaseModel):
    title: str = Field(min_length=5, max_length=140)
    query: str = Field(min_length=2, max_length=200)
    platforms: List[Platform] = Field(default_factory=lambda: [
        Platform.x,
        Platform.telegram,
        Platform.youtube,
        Platform.instagram,
        Platform.web,
    ])


class ContentItem(BaseModel):
    id: str
    case_id: str
    platform: Platform
    author: str
    text: str
    url: str
    observed_at: datetime
    language: str
    engagement: int
    source_name: str
    media_hash: Optional[str] = None
    narrative_key: Optional[str] = None
    entities: List[str] = Field(default_factory=list)


class RiskSignals(BaseModel):
    harm: float = 0.0
    velocity: float = 0.0
    reach: float = 0.0
    coordination: float = 0.0
    credibility_gap: float = 0.0
    cross_platform: float = 0.0


class AnalysisResult(BaseModel):
    signals: RiskSignals
    score: float
    severity: Severity
    narrative_clusters: Dict[str, int] = Field(default_factory=dict)
    top_entities: List[str] = Field(default_factory=list)
    top_accounts: List[str] = Field(default_factory=list)
    language_distribution: Dict[str, int] = Field(default_factory=dict)
    generated_at: datetime


class CaseRecord(BaseModel):
    id: str
    title: str
    query: str
    platforms: List[Platform]
    status: Status
    created_at: datetime
    updated_at: datetime
    item_count: int = 0
    risk_score: float = 0.0
    severity: Severity = Severity.r1
    analysis: Optional[AnalysisResult] = None


class CaseGraph(BaseModel):
    nodes: List[Dict[str, str]]
    edges: List[Dict[str, str]]


class AlertRecord(BaseModel):
    id: str
    case_id: str
    severity: Severity
    status: AlertStatus
    title: str
    summary: str
    recommended_action: str
    created_at: datetime


class EvidenceRecord(BaseModel):
    id: str
    case_id: str
    item_id: str
    source_name: str
    source_url: str
    evidence_hash: str
    note: str
    captured_at: datetime


class TimelineEvent(BaseModel):
    id: str
    case_id: str
    event_type: str
    summary: str
    created_at: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ConnectorStatus(BaseModel):
    connector: str
    domain: str
    health: str
    success_rate: float
    avg_latency_ms: int
    last_error: Optional[str] = None


class SourceCatalogEntry(BaseModel):
    id: str
    name: str
    category: str
    source_type: str
    origin_repo: str
    url: str
    tags: List[str] = Field(default_factory=list)


class MediaVerificationResult(BaseModel):
    item_id: str
    verdict: VerificationVerdict
    confidence: float
    checks: Dict[str, bool]
    explanation: str


class CaseReport(BaseModel):
    case_id: str
    headline: str
    executive_summary: List[str]
    findings: List[str]
    recommendations: List[str]
    generated_at: datetime


class GlobalMetrics(BaseModel):
    total_cases: int
    open_alerts: int
    avg_risk: float
    high_severity_cases: int
