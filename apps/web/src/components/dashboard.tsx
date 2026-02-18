"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

import {
  analyzeCase,
  collectCase,
  createCase,
  generateProducts,
  getCaseAlerts,
  getCaseEvidence,
  getCaseGraph,
  getCaseItems,
  getCaseMediaVerification,
  getCaseReport,
  getCaseTimeline,
  getConnectorStatus,
  getGlobalMetrics,
  getSourceCatalog,
  listCases,
  runAllCase,
} from "@/lib/api";
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

const PLATFORM_OPTIONS: Platform[] = ["x", "telegram", "youtube", "instagram", "web"];

const SEVERITY_STYLES: Record<string, string> = {
  R1: "bg-emerald-100 text-emerald-900",
  R2: "bg-amber-100 text-amber-900",
  R3: "bg-orange-100 text-orange-900",
  R4: "bg-rose-100 text-rose-900",
};

const VERDICT_STYLES: Record<string, string> = {
  likely_authentic: "bg-emerald-100 text-emerald-800",
  suspicious: "bg-amber-100 text-amber-800",
  reused: "bg-rose-100 text-rose-800",
};

const EMPTY_METRICS: GlobalMetrics = {
  total_cases: 0,
  open_alerts: 0,
  avg_risk: 0,
  high_severity_cases: 0,
};

function RiskSignalBar({ label, value }: { label: string; value: number }) {
  return (
    <div className="space-y-1">
      <div className="flex items-center justify-between text-xs text-slate-600">
        <span>{label}</span>
        <span>{value.toFixed(1)}</span>
      </div>
      <div className="h-2 rounded-full bg-slate-200">
        <div className="h-2 rounded-full bg-slate-800" style={{ width: `${Math.min(100, value)}%` }} />
      </div>
    </div>
  );
}

export default function Dashboard() {
  const [cases, setCases] = useState<CaseRecord[]>([]);
  const [title, setTitle] = useState("MENA Narrative Pulse");
  const [query, setQuery] = useState("regional misinformation wave");
  const [platforms, setPlatforms] = useState<Platform[]>(PLATFORM_OPTIONS);
  const [activeCaseId, setActiveCaseId] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>("");

  const [graph, setGraph] = useState<GraphData | null>(null);
  const [items, setItems] = useState<ContentItem[]>([]);
  const [alerts, setAlerts] = useState<AlertRecord[]>([]);
  const [evidence, setEvidence] = useState<EvidenceRecord[]>([]);
  const [timeline, setTimeline] = useState<TimelineEvent[]>([]);
  const [mediaChecks, setMediaChecks] = useState<MediaVerificationResult[]>([]);
  const [report, setReport] = useState<CaseReport | null>(null);

  const [globalMetrics, setGlobalMetrics] = useState<GlobalMetrics>(EMPTY_METRICS);
  const [connectors, setConnectors] = useState<ConnectorStatus[]>([]);
  const [catalog, setCatalog] = useState<SourceCatalogEntry[]>([]);

  const activeCase = useMemo(() => cases.find((entry) => entry.id === activeCaseId), [cases, activeCaseId]);

  const refreshCases = useCallback(async () => {
    setError("");
    try {
      const [caseData, metricsData, connectorData, catalogData] = await Promise.all([
        listCases(),
        getGlobalMetrics(),
        getConnectorStatus(),
        getSourceCatalog(),
      ]);
      setCases(caseData);
      setGlobalMetrics(metricsData);
      setConnectors(connectorData);
      setCatalog(catalogData);
      if (!activeCaseId && caseData.length > 0) {
        setActiveCaseId(caseData[0].id);
      }
    } catch {
      setError("API is unavailable. Ensure backend is running and reachable.");
    }
  }, [activeCaseId]);

  useEffect(() => {
    void refreshCases();
  }, [refreshCases]);

  useEffect(() => {
    if (!activeCaseId) {
      setGraph(null);
      setItems([]);
      setAlerts([]);
      setEvidence([]);
      setTimeline([]);
      setMediaChecks([]);
      setReport(null);
      return;
    }

    async function loadCaseProducts() {
      const [graphData, itemData, alertData, evidenceData, timelineData, mediaData, reportData] =
        await Promise.all([
          getCaseGraph(activeCaseId).catch(() => null),
          getCaseItems(activeCaseId).catch(() => []),
          getCaseAlerts(activeCaseId).catch(() => []),
          getCaseEvidence(activeCaseId).catch(() => []),
          getCaseTimeline(activeCaseId).catch(() => []),
          getCaseMediaVerification(activeCaseId).catch(() => []),
          getCaseReport(activeCaseId).catch(() => null),
        ]);
      setGraph(graphData);
      setItems(itemData);
      setAlerts(alertData);
      setEvidence(evidenceData);
      setTimeline(timelineData);
      setMediaChecks(mediaData);
      setReport(reportData);
    }

    void loadCaseProducts();
  }, [activeCaseId, cases]);

  function togglePlatform(platform: Platform) {
    setPlatforms((prev) => (prev.includes(platform) ? prev.filter((item) => item !== platform) : [...prev, platform]));
  }

  async function handleCreateCase() {
    if (!title.trim() || !query.trim() || platforms.length === 0) {
      return;
    }
    setLoading(true);
    setError("");
    try {
      const created = await createCase({ title, query, platforms });
      setActiveCaseId(created.id);
      await refreshCases();
    } catch {
      setError("Failed to create a new case.");
    } finally {
      setLoading(false);
    }
  }

  async function runCaseAction(caseId: string, action: "collect" | "analyze" | "runall" | "products") {
    setLoading(true);
    setError("");
    try {
      if (action === "collect") {
        await collectCase(caseId);
      } else if (action === "analyze") {
        await analyzeCase(caseId);
      } else if (action === "runall") {
        await runAllCase(caseId);
      } else {
        await generateProducts(caseId);
      }
      setActiveCaseId(caseId);
      await refreshCases();
    } catch {
      setError("Action failed. Retry after checking API logs.");
    } finally {
      setLoading(false);
    }
  }

  const localMetrics = useMemo(() => {
    const totalItems = cases.reduce((acc, entry) => acc + entry.item_count, 0);
    return {
      totalItems,
      avgRisk: globalMetrics.avg_risk,
      highSeverity: globalMetrics.high_severity_cases,
      openAlerts: globalMetrics.open_alerts,
    };
  }, [cases, globalMetrics]);

  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_15%_15%,#fde68a_0%,#ffedd5_30%,#f8fafc_100%)] px-4 py-8 text-slate-900 md:px-10">
      <div className="mx-auto max-w-7xl space-y-8">
        <header className="rounded-3xl border border-slate-200 bg-white/80 p-6 shadow-sm backdrop-blur-sm md:p-8">
          <p className="inline-block rounded-full bg-slate-900 px-3 py-1 text-xs font-semibold uppercase tracking-[0.22em] text-slate-50">
            Nexus MENA OSINT
          </p>
          <h1 className="mt-4 max-w-5xl text-3xl font-semibold leading-tight md:text-5xl">
            Unified Intelligence Platform: Collection, Graph Analysis, Risk Alerts, Evidence, and Reporting
          </h1>
          <p className="mt-4 max-w-4xl text-sm text-slate-600 md:text-base">
            End-to-end disinformation operations for MENA with Arabic-English narrative linking, coordinated behavior
            detection, media verification, case workflows, and analyst-ready outputs in one platform.
          </p>
          {error ? <p className="mt-3 text-sm text-rose-700">{error}</p> : null}
        </header>

        <section className="grid gap-4 md:grid-cols-4">
          <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <p className="text-xs uppercase tracking-widest text-slate-500">Average Risk</p>
            <p className="mt-3 text-3xl font-semibold">{localMetrics.avgRisk}</p>
          </div>
          <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <p className="text-xs uppercase tracking-widest text-slate-500">Open Alerts</p>
            <p className="mt-3 text-3xl font-semibold">{localMetrics.openAlerts}</p>
          </div>
          <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <p className="text-xs uppercase tracking-widest text-slate-500">High Severity Cases</p>
            <p className="mt-3 text-3xl font-semibold">{localMetrics.highSeverity}</p>
          </div>
          <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <p className="text-xs uppercase tracking-widest text-slate-500">Collected Items</p>
            <p className="mt-3 text-3xl font-semibold">{localMetrics.totalItems}</p>
          </div>
        </section>

        <section className="grid gap-6 lg:grid-cols-[1.1fr_1.9fr]">
          <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <h2 className="text-xl font-semibold">Create Investigation Case</h2>
            <div className="mt-4 space-y-3">
              <input
                value={title}
                onChange={(event) => setTitle(event.target.value)}
                placeholder="Case title"
                className="w-full rounded-xl border border-slate-300 px-3 py-2 text-sm outline-none ring-0 focus:border-slate-700"
              />
              <textarea
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                placeholder="Search query"
                className="min-h-24 w-full rounded-xl border border-slate-300 px-3 py-2 text-sm outline-none ring-0 focus:border-slate-700"
              />
              <div className="flex flex-wrap gap-2">
                {PLATFORM_OPTIONS.map((platform) => (
                  <button
                    key={platform}
                    onClick={() => togglePlatform(platform)}
                    className={`rounded-full border px-3 py-1 text-xs font-semibold uppercase tracking-wide transition ${
                      platforms.includes(platform)
                        ? "border-slate-900 bg-slate-900 text-white"
                        : "border-slate-300 bg-white text-slate-700"
                    }`}
                  >
                    {platform}
                  </button>
                ))}
              </div>
              <button
                disabled={loading || platforms.length === 0}
                onClick={() => void handleCreateCase()}
                className="w-full rounded-xl bg-slate-900 px-4 py-2 text-sm font-semibold text-white transition hover:bg-slate-700 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {loading ? "Working..." : "Create Case"}
              </button>
            </div>
          </div>

          <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-semibold">Investigation Board</h2>
              <button
                onClick={() => void refreshCases()}
                className="rounded-full border border-slate-300 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-slate-700"
              >
                Refresh
              </button>
            </div>

            <div className="mt-4 grid gap-3">
              {cases.length === 0 ? (
                <div className="rounded-xl border border-dashed border-slate-300 p-6 text-sm text-slate-500">
                  No cases yet. Create your first investigation case.
                </div>
              ) : (
                cases.map((entry) => (
                  <article
                    key={entry.id}
                    className={`rounded-xl border p-4 transition ${
                      activeCaseId === entry.id ? "border-slate-900" : "border-slate-200"
                    }`}
                  >
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <button
                        onClick={() => setActiveCaseId(entry.id)}
                        className="text-left text-sm font-semibold text-slate-900"
                      >
                        {entry.title}
                      </button>
                      <span className={`rounded-full px-2 py-1 text-xs font-semibold ${SEVERITY_STYLES[entry.severity]}`}>
                        {entry.severity}
                      </span>
                    </div>
                    <p className="mt-2 text-xs text-slate-600">{entry.query}</p>
                    <div className="mt-3 flex flex-wrap gap-2 text-xs text-slate-600">
                      <span>Items: {entry.item_count}</span>
                      <span>Risk: {entry.risk_score}</span>
                      <span>Status: {entry.status}</span>
                    </div>
                    <div className="mt-3 flex flex-wrap gap-2">
                      <button
                        onClick={() => void runCaseAction(entry.id, "collect")}
                        disabled={loading}
                        className="rounded-lg border border-slate-300 px-3 py-1 text-xs font-semibold"
                      >
                        Collect
                      </button>
                      <button
                        onClick={() => void runCaseAction(entry.id, "analyze")}
                        disabled={loading || entry.item_count === 0}
                        className="rounded-lg bg-slate-900 px-3 py-1 text-xs font-semibold text-white disabled:opacity-50"
                      >
                        Analyze
                      </button>
                      <button
                        onClick={() => void runCaseAction(entry.id, "products")}
                        disabled={loading || !entry.analysis}
                        className="rounded-lg border border-slate-900 px-3 py-1 text-xs font-semibold text-slate-900 disabled:opacity-50"
                      >
                        Products
                      </button>
                      <button
                        onClick={() => void runCaseAction(entry.id, "runall")}
                        disabled={loading}
                        className="rounded-lg bg-amber-200 px-3 py-1 text-xs font-semibold text-amber-900 disabled:opacity-50"
                      >
                        Run All
                      </button>
                    </div>
                  </article>
                ))
              )}
            </div>
          </div>
        </section>

        <section className="grid gap-6 xl:grid-cols-[1.3fr_1fr]">
          <div className="space-y-6">
            <article className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
              <h2 className="text-xl font-semibold">Narrative & Risk Intelligence</h2>
              {activeCase?.analysis ? (
                <div className="mt-4 space-y-4">
                  <div className="grid gap-3 md:grid-cols-2">
                    <div className="rounded-xl border border-slate-200 p-3">
                      <p className="text-xs uppercase tracking-wide text-slate-500">Top Narrative Clusters</p>
                      <ul className="mt-2 space-y-1 text-sm">
                        {Object.entries(activeCase.analysis.narrative_clusters).map(([key, value]) => (
                          <li key={key} className="flex justify-between">
                            <span>{key}</span>
                            <span className="font-semibold">{value}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                    <div className="rounded-xl border border-slate-200 p-3">
                      <p className="text-xs uppercase tracking-wide text-slate-500">Language Distribution</p>
                      <ul className="mt-2 space-y-1 text-sm">
                        {Object.entries(activeCase.analysis.language_distribution).map(([lang, value]) => (
                          <li key={lang} className="flex justify-between">
                            <span>{lang}</span>
                            <span className="font-semibold">{value}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                  <div className="grid gap-3 md:grid-cols-2">
                    <RiskSignalBar label="Harm" value={activeCase.analysis.signals.harm} />
                    <RiskSignalBar label="Velocity" value={activeCase.analysis.signals.velocity} />
                    <RiskSignalBar label="Reach" value={activeCase.analysis.signals.reach} />
                    <RiskSignalBar label="Coordination" value={activeCase.analysis.signals.coordination} />
                    <RiskSignalBar label="Credibility Gap" value={activeCase.analysis.signals.credibility_gap} />
                    <RiskSignalBar label="Cross Platform" value={activeCase.analysis.signals.cross_platform} />
                  </div>
                </div>
              ) : (
                <p className="mt-3 text-sm text-slate-500">Analyze the active case to generate intelligence signals.</p>
              )}
            </article>

            <article className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
              <h2 className="text-xl font-semibold">Intelligence Products</h2>
              <div className="mt-4 grid gap-4 md:grid-cols-2">
                <div>
                  <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-500">Alerts</h3>
                  <ul className="mt-2 max-h-56 space-y-2 overflow-auto text-sm">
                    {alerts.length === 0 ? <li className="text-slate-500">No alerts generated yet.</li> : null}
                    {alerts.map((alert) => (
                      <li key={alert.id} className="rounded-lg border border-slate-200 p-2">
                        <p className="font-semibold">{alert.title}</p>
                        <p className="mt-1 text-xs text-slate-600">{alert.summary}</p>
                        <p className="mt-1 text-xs text-slate-500">Action: {alert.recommended_action}</p>
                      </li>
                    ))}
                  </ul>
                </div>
                <div>
                  <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-500">Evidence</h3>
                  <ul className="mt-2 max-h-56 space-y-2 overflow-auto text-sm">
                    {evidence.length === 0 ? <li className="text-slate-500">No evidence package generated yet.</li> : null}
                    {evidence.slice(0, 20).map((entry) => (
                      <li key={entry.id} className="rounded-lg border border-slate-200 p-2">
                        <p className="font-medium">{entry.source_name}</p>
                        <p className="mt-1 break-all text-xs text-slate-500">{entry.evidence_hash.slice(0, 18)}...</p>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </article>

            <article className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
              <h2 className="text-xl font-semibold">Graph & Timeline</h2>
              <div className="mt-4 grid gap-4 md:grid-cols-2">
                <div>
                  <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-500">Graph Nodes</h3>
                  <ul className="mt-2 max-h-52 space-y-1 overflow-auto text-sm">
                    {(graph?.nodes ?? []).slice(0, 20).map((node) => (
                      <li key={node.id} className="rounded-md bg-slate-100 px-2 py-1">
                        {node.label} <span className="text-xs text-slate-500">({node.type})</span>
                      </li>
                    ))}
                  </ul>
                </div>
                <div>
                  <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-500">Timeline</h3>
                  <ul className="mt-2 max-h-52 space-y-2 overflow-auto text-sm">
                    {timeline.length === 0 ? <li className="text-slate-500">No timeline events yet.</li> : null}
                    {timeline.map((event) => (
                      <li key={event.id} className="rounded-lg border border-slate-200 p-2">
                        <p className="font-medium">{event.event_type}</p>
                        <p className="text-xs text-slate-600">{event.summary}</p>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </article>

            <article className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
              <h2 className="text-xl font-semibold">Media Verification</h2>
              <ul className="mt-3 grid gap-2 text-sm md:grid-cols-2">
                {mediaChecks.length === 0 ? <li className="text-slate-500">No media checks available yet.</li> : null}
                {mediaChecks.map((entry) => (
                  <li key={entry.item_id} className="rounded-lg border border-slate-200 p-3">
                    <div className="flex items-center justify-between gap-2">
                      <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">{entry.item_id}</p>
                      <span className={`rounded-full px-2 py-1 text-xs font-semibold ${VERDICT_STYLES[entry.verdict]}`}>
                        {entry.verdict}
                      </span>
                    </div>
                    <p className="mt-2 text-xs text-slate-600">{entry.explanation}</p>
                    <p className="mt-2 text-xs text-slate-500">Confidence: {(entry.confidence * 100).toFixed(0)}%</p>
                  </li>
                ))}
              </ul>
            </article>
          </div>

          <div className="space-y-6">
            <article className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
              <h2 className="text-xl font-semibold">Case Report</h2>
              {report ? (
                <div className="mt-3 space-y-3 text-sm">
                  <p className="font-semibold">{report.headline}</p>
                  <div>
                    <p className="text-xs uppercase tracking-wide text-slate-500">Executive Summary</p>
                    <ul className="mt-1 list-disc space-y-1 pl-5 text-slate-700">
                      {report.executive_summary.map((line) => (
                        <li key={line}>{line}</li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <p className="text-xs uppercase tracking-wide text-slate-500">Recommendations</p>
                    <ul className="mt-1 list-disc space-y-1 pl-5 text-slate-700">
                      {report.recommendations.map((line) => (
                        <li key={line}>{line}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              ) : (
                <p className="mt-3 text-sm text-slate-500">No report yet. Run analysis or generate products.</p>
              )}
            </article>

            <article className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
              <h2 className="text-xl font-semibold">Connector Health</h2>
              <ul className="mt-3 space-y-2 text-sm">
                {connectors.map((connector) => (
                  <li key={connector.connector} className="rounded-lg border border-slate-200 p-2">
                    <div className="flex items-center justify-between gap-2">
                      <p className="font-medium">{connector.connector}</p>
                      <span
                        className={`rounded-full px-2 py-1 text-xs font-semibold ${
                          connector.health === "healthy"
                            ? "bg-emerald-100 text-emerald-800"
                            : "bg-amber-100 text-amber-800"
                        }`}
                      >
                        {connector.health}
                      </span>
                    </div>
                    <p className="mt-1 text-xs text-slate-600">
                      Success {(connector.success_rate * 100).toFixed(0)}% · Avg {connector.avg_latency_ms}ms
                    </p>
                  </li>
                ))}
              </ul>
            </article>

            <article className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
              <h2 className="text-xl font-semibold">Source Catalog</h2>
              <ul className="mt-3 max-h-72 space-y-2 overflow-auto text-sm">
                {catalog.map((source) => (
                  <li key={source.id} className="rounded-lg border border-slate-200 p-2">
                    <p className="font-medium">{source.name}</p>
                    <p className="mt-1 text-xs text-slate-600">{source.origin_repo}</p>
                    <p className="mt-1 text-xs text-slate-500">{source.tags.join(" · ")}</p>
                  </li>
                ))}
              </ul>
            </article>

            <article className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
              <h2 className="text-xl font-semibold">Top Case Signals</h2>
              {activeCase?.analysis ? (
                <div className="mt-3 space-y-2 text-sm">
                  <p>
                    <strong>Top entities:</strong> {activeCase.analysis.top_entities.join(", ") || "none"}
                  </p>
                  <p>
                    <strong>Top accounts:</strong> {activeCase.analysis.top_accounts.join(", ") || "none"}
                  </p>
                  <p>
                    <strong>Case items:</strong> {items.length}
                  </p>
                </div>
              ) : (
                <p className="mt-3 text-sm text-slate-500">Select and analyze a case to see key signals.</p>
              )}
            </article>
          </div>
        </section>
      </div>
    </div>
  );
}
