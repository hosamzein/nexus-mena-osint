export type Platform = "x" | "telegram" | "youtube" | "instagram" | "web";

export type Severity = "R1" | "R2" | "R3" | "R4";

export type Status = "draft" | "collecting" | "analyzing" | "ready";

export interface RiskSignals {
  harm: number;
  velocity: number;
  reach: number;
  coordination: number;
  credibility_gap: number;
  cross_platform: number;
}

export interface AnalysisResult {
  signals: RiskSignals;
  score: number;
  severity: Severity;
  narrative_clusters: Record<string, number>;
  top_entities: string[];
  generated_at: string;
}

export interface CaseRecord {
  id: string;
  title: string;
  query: string;
  platforms: Platform[];
  status: Status;
  created_at: string;
  updated_at: string;
  item_count: number;
  risk_score: number;
  severity: Severity;
  analysis?: AnalysisResult;
}

export interface GraphData {
  nodes: { id: string; label: string; type: string }[];
  edges: { source: string; target: string; type: string }[];
}
