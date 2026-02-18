import {
  AlertRecord,
  CaseRecord,
  CaseReport,
  ConnectorStatus,
  ContentItem,
  EvidenceRecord,
  GlobalMetrics,
  GraphData,
  MediaVerificationResult,
  Platform,
  SourceCatalogEntry,
  TimelineEvent,
} from "@/lib/types";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
    cache: "no-store",
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || "Request failed");
  }

  return (await response.json()) as T;
}

export function listCases(): Promise<CaseRecord[]> {
  return request<CaseRecord[]>("/api/v1/cases");
}

export function createCase(payload: {
  title: string;
  query: string;
  platforms: Platform[];
}): Promise<CaseRecord> {
  return request<CaseRecord>("/api/v1/cases", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function collectCase(caseId: string): Promise<CaseRecord> {
  return request<CaseRecord>(`/api/v1/cases/${caseId}/collect`, {
    method: "POST",
  });
}

export function analyzeCase(caseId: string): Promise<CaseRecord> {
  return request<CaseRecord>(`/api/v1/cases/${caseId}/analyze`, {
    method: "POST",
  });
}

export function runAllCase(caseId: string): Promise<CaseRecord> {
  return request<CaseRecord>(`/api/v1/cases/${caseId}/run-all`, {
    method: "POST",
  });
}

export function generateProducts(caseId: string): Promise<CaseRecord> {
  return request<CaseRecord>(`/api/v1/cases/${caseId}/generate-products`, {
    method: "POST",
  });
}

export function getCaseGraph(caseId: string): Promise<GraphData> {
  return request<GraphData>(`/api/v1/cases/${caseId}/graph`);
}

export function getCaseItems(caseId: string): Promise<ContentItem[]> {
  return request<ContentItem[]>(`/api/v1/cases/${caseId}/items`);
}

export function getCaseAlerts(caseId: string): Promise<AlertRecord[]> {
  return request<AlertRecord[]>(`/api/v1/cases/${caseId}/alerts`);
}

export function getCaseEvidence(caseId: string): Promise<EvidenceRecord[]> {
  return request<EvidenceRecord[]>(`/api/v1/cases/${caseId}/evidence`);
}

export function getCaseTimeline(caseId: string): Promise<TimelineEvent[]> {
  return request<TimelineEvent[]>(`/api/v1/cases/${caseId}/timeline`);
}

export function getCaseMediaVerification(caseId: string): Promise<MediaVerificationResult[]> {
  return request<MediaVerificationResult[]>(`/api/v1/cases/${caseId}/media-verification`);
}

export function getCaseReport(caseId: string): Promise<CaseReport> {
  return request<CaseReport>(`/api/v1/cases/${caseId}/report`);
}

export function getGlobalMetrics(): Promise<GlobalMetrics> {
  return request<GlobalMetrics>("/api/v1/metrics");
}

export function getConnectorStatus(): Promise<ConnectorStatus[]> {
  return request<ConnectorStatus[]>("/api/v1/connectors");
}

export function getSourceCatalog(): Promise<SourceCatalogEntry[]> {
  return request<SourceCatalogEntry[]>("/api/v1/source-catalog");
}
