import { CaseRecord, GraphData, Platform } from "@/lib/types";

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

export function getCaseGraph(caseId: string): Promise<GraphData> {
  return request<GraphData>(`/api/v1/cases/${caseId}/graph`);
}
