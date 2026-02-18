from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .analysis import analyze_items
from .connectors import build_case_graph, collect_case_items
from .schemas import CaseGraph, CaseRecord, CreateCaseRequest, Status
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
    return store.save_analysis(case_id, analysis.score, analysis.severity, analysis)


@app.get("/api/v1/cases/{case_id}/graph", response_model=CaseGraph)
def graph(case_id: str) -> CaseGraph:
    try:
        store.get_case(case_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Case not found")

    graph_data = build_case_graph(store.get_items(case_id))
    return CaseGraph(nodes=graph_data["nodes"], edges=graph_data["edges"])
