from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .analysis import analyze_items
from .connectors import (
    build_case_graph,
    collect_case_items,
    list_connector_health,
    list_source_catalog,
)
from .intelligence import build_alerts, build_case_report, build_evidence, verify_media
from .schemas import (
    AlertRecord,
    CaseGraph,
    CaseRecord,
    CaseReport,
    ConnectorStatus,
    ContentItem,
    CreateCaseRequest,
    EvidenceRecord,
    GlobalMetrics,
    MediaVerificationResult,
    SourceCatalogEntry,
    Status,
    TimelineEvent,
)
from .storage import store


app = FastAPI(
    title="Nexus MENA OSINT API",
    version="0.1.0",
    description="Multidomain OSINT API for disinformation and risk monitoring.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "service": "nexus-mena-osint-api",
        "time": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/api/v1/cases", response_model=list[CaseRecord])
def list_cases() -> list[CaseRecord]:
    return store.list_cases()


@app.post("/api/v1/cases", response_model=CaseRecord)
def create_case(payload: CreateCaseRequest) -> CaseRecord:
    case = CaseRecord(
        id=f"case_{uuid4().hex[:10]}",
        title=payload.title,
        query=payload.query,
        platforms=payload.platforms,
        status=Status.draft,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    return store.create_case(case)


@app.get("/api/v1/cases/{case_id}", response_model=CaseRecord)
def get_case(case_id: str) -> CaseRecord:
    try:
        return store.get_case(case_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Case not found")


@app.post("/api/v1/cases/{case_id}/collect", response_model=CaseRecord)
def collect(case_id: str) -> CaseRecord:
    try:
        case = store.get_case(case_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Case not found")

    new_items = collect_case_items(case.id, case.query, case.platforms)
    return store.append_items(case_id, new_items)


@app.post("/api/v1/cases/{case_id}/analyze", response_model=CaseRecord)
def analyze(case_id: str) -> CaseRecord:
    try:
        case = store.get_case(case_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Case not found")

    case.status = Status.analyzing
    items = store.get_items(case_id)
    analysis = analyze_items(items)
    case = store.save_analysis(case_id, analysis.score, analysis.severity, analysis)
    alerts = build_alerts(case_id, analysis)
    evidence = build_evidence(case_id, items)
    media_results = verify_media(items)
    report = build_case_report(case_id, analysis, items)
    store.save_alerts(case_id, alerts)
    store.save_evidence(case_id, evidence)
    store.save_media_verification(case_id, media_results)
    store.save_report(case_id, report)
    return case


@app.get("/api/v1/cases/{case_id}/graph", response_model=CaseGraph)
def graph(case_id: str) -> CaseGraph:
    try:
        store.get_case(case_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Case not found")

    graph_data = build_case_graph(store.get_items(case_id))
    return CaseGraph(nodes=graph_data["nodes"], edges=graph_data["edges"])


@app.get("/api/v1/cases/{case_id}/items", response_model=list[ContentItem])
def case_items(case_id: str) -> list[ContentItem]:
    try:
        store.get_case(case_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Case not found")
    return store.get_items(case_id)


@app.get("/api/v1/cases/{case_id}/alerts", response_model=list[AlertRecord])
def case_alerts(case_id: str) -> list[AlertRecord]:
    try:
        store.get_case(case_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Case not found")
    return store.get_alerts(case_id)


@app.get("/api/v1/cases/{case_id}/evidence", response_model=list[EvidenceRecord])
def case_evidence(case_id: str) -> list[EvidenceRecord]:
    try:
        store.get_case(case_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Case not found")
    return store.get_evidence(case_id)


@app.get("/api/v1/cases/{case_id}/timeline", response_model=list[TimelineEvent])
def case_timeline(case_id: str) -> list[TimelineEvent]:
    try:
        store.get_case(case_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Case not found")
    return store.get_timeline(case_id)


@app.get("/api/v1/cases/{case_id}/media-verification", response_model=list[MediaVerificationResult])
def case_media_verification(case_id: str) -> list[MediaVerificationResult]:
    try:
        store.get_case(case_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Case not found")
    return store.get_media_verification(case_id)


@app.get("/api/v1/cases/{case_id}/report", response_model=CaseReport)
def case_report(case_id: str) -> CaseReport:
    try:
        store.get_case(case_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Case not found")
    report = store.get_report(case_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not generated")
    return report


@app.get("/api/v1/connectors", response_model=list[ConnectorStatus])
def connectors() -> list[ConnectorStatus]:
    return list_connector_health()


@app.get("/api/v1/source-catalog", response_model=list[SourceCatalogEntry])
def source_catalog() -> list[SourceCatalogEntry]:
    return list_source_catalog()


@app.get("/api/v1/metrics", response_model=GlobalMetrics)
def global_metrics() -> GlobalMetrics:
    return store.get_global_metrics()


@app.post("/api/v1/cases/{case_id}/run-all", response_model=CaseRecord)
def run_all(case_id: str) -> CaseRecord:
    try:
        case = store.get_case(case_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Case not found")

    new_items = collect_case_items(case.id, case.query, case.platforms)
    case = store.append_items(case_id, new_items)
    analysis = analyze_items(store.get_items(case_id))
    case = store.save_analysis(case_id, analysis.score, analysis.severity, analysis)
    alerts = build_alerts(case_id, analysis)
    evidence = build_evidence(case_id, store.get_items(case_id))
    media_results = verify_media(store.get_items(case_id))
    report = build_case_report(case_id, analysis, store.get_items(case_id))
    store.save_alerts(case_id, alerts)
    store.save_evidence(case_id, evidence)
    store.save_media_verification(case_id, media_results)
    store.save_report(case_id, report)
    return case


@app.post("/api/v1/cases/{case_id}/generate-products", response_model=CaseRecord)
def generate_products(case_id: str) -> CaseRecord:
    try:
        case = store.get_case(case_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Case not found")

    if not case.analysis:
        raise HTTPException(status_code=400, detail="Analyze the case first")

    alerts = build_alerts(case_id, case.analysis)
    evidence = build_evidence(case_id, store.get_items(case_id))
    media_results = verify_media(store.get_items(case_id))
    report = build_case_report(case_id, case.analysis, store.get_items(case_id))
    store.save_alerts(case_id, alerts)
    store.save_evidence(case_id, evidence)
    store.save_media_verification(case_id, media_results)
    store.save_report(case_id, report)
    case.updated_at = datetime.now(timezone.utc)
    return case
