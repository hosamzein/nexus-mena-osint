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
  top_accounts: string[];
  language_distribution: Record<string, number>;
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

export interface ContentItem {
  id: string;
  case_id: string;
  platform: Platform;
  author: string;
  text: string;
  url: string;
  observed_at: string;
  language: string;
  engagement: number;
  source_name: string;
  media_hash?: string;
  narrative_key?: string;
  entities: string[];
}

export interface AlertRecord {
  id: string;
  case_id: string;
  severity: Severity;
  status: "open" | "triaged" | "closed";
  title: string;
  summary: string;
  recommended_action: string;
  created_at: string;
}

export interface EvidenceRecord {
  id: string;
  case_id: string;
  item_id: string;
  source_name: string;
  source_url: string;
  evidence_hash: string;
  note: string;
  captured_at: string;
}

export interface TimelineEvent {
  id: string;
  case_id: string;
  event_type: string;
  summary: string;
  created_at: string;
  metadata: Record<string, string | number | boolean>;
}

export interface MediaVerificationResult {
  item_id: string;
  verdict: "likely_authentic" | "suspicious" | "reused";
  confidence: number;
  checks: Record<string, boolean>;
  explanation: string;
}

export interface CaseReport {
  case_id: string;
  headline: string;
  executive_summary: string[];
  findings: string[];
  recommendations: string[];
  generated_at: string;
}

export interface ConnectorStatus {
  connector: string;
  domain: string;
  health: string;
  success_rate: number;
  avg_latency_ms: number;
  last_error?: string;
}

export interface SourceCatalogEntry {
  id: string;
  name: string;
  category: string;
  source_type: string;
  origin_repo: string;
  url: string;
  tags: string[];
}

export interface GlobalMetrics {
  total_cases: number;
  open_alerts: number;
  avg_risk: number;
  high_severity_cases: number;
}
