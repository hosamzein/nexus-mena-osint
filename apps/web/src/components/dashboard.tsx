"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

import { analyzeCase, collectCase, createCase, getCaseGraph, listCases } from "@/lib/api";
import { CaseRecord, GraphData, Platform } from "@/lib/types";

const PLATFORM_OPTIONS: Platform[] = [
  "x",
  "telegram",
  "youtube",
  "instagram",
  "web",
];

const SEVERITY_STYLES: Record<string, string> = {
  R1: "bg-emerald-100 text-emerald-900",
  R2: "bg-amber-100 text-amber-900",
  R3: "bg-orange-100 text-orange-900",
  R4: "bg-rose-100 text-rose-900",
};

export default function Dashboard() {
  const [cases, setCases] = useState<CaseRecord[]>([]);
  const [title, setTitle] = useState("MENA Narrative Pulse");
  const [query, setQuery] = useState("regional misinformation wave");
  const [platforms, setPlatforms] = useState<Platform[]>(PLATFORM_OPTIONS);
  const [loading, setLoading] = useState(false);
  const [activeCaseId, setActiveCaseId] = useState<string>("");
  const [graph, setGraph] = useState<GraphData | null>(null);
  const [error, setError] = useState<string>("");

  const refresh = useCallback(async () => {
    setError("");
    try {
      const data = await listCases();
      setCases(data);
      if (!activeCaseId && data.length > 0) {
        setActiveCaseId(data[0].id);
      }
    } catch {
      setError("Could not reach API. Start FastAPI on http://localhost:8000.");
    }
  }, [activeCaseId]);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  useEffect(() => {
    if (!activeCaseId) return;
    void getCaseGraph(activeCaseId).then(setGraph).catch(() => setGraph(null));
  }, [activeCaseId, cases]);

  const metrics = useMemo(() => {
    if (!cases.length) {
      return { avgRisk: 0, r3r4: 0, totalItems: 0 };
    }
    const avgRisk =
      cases.reduce((acc, item) => acc + item.risk_score, 0) / Math.max(cases.length, 1);
    const r3r4 = cases.filter((item) => item.severity === "R3" || item.severity === "R4").length;
    const totalItems = cases.reduce((acc, item) => acc + item.item_count, 0);
    return { avgRisk: Math.round(avgRisk), r3r4, totalItems };
  }, [cases]);

  async function handleCreateCase() {
    if (!title.trim() || !query.trim()) return;
    setLoading(true);
    setError("");
    try {
      await createCase({ title, query, platforms });
      await refresh();
    } catch {
      setError("Failed to create case.");
    } finally {
      setLoading(false);
    }
  }

  async function handleCollect(caseId: string) {
    setLoading(true);
    setError("");
    try {
      await collectCase(caseId);
      await refresh();
      setActiveCaseId(caseId);
    } catch {
      setError("Failed to collect intelligence.");
    } finally {
      setLoading(false);
    }
  }

  async function handleAnalyze(caseId: string) {
    setLoading(true);
    setError("");
    try {
      await analyzeCase(caseId);
      await refresh();
      setActiveCaseId(caseId);
    } catch {
      setError("Failed to analyze case.");
    } finally {
      setLoading(false);
    }
  }

  function togglePlatform(value: Platform) {
    setPlatforms((prev) =>
      prev.includes(value) ? prev.filter((item) => item !== value) : [...prev, value]
    );
  }

  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_10%_10%,#fef3c7_0%,#fff7ed_35%,#f8fafc_100%)] px-5 py-8 text-slate-900 md:px-10">
      <div className="mx-auto max-w-7xl space-y-8">
        <header className="rounded-3xl border border-slate-200/70 bg-white/80 p-6 shadow-sm backdrop-blur-sm md:p-8">
          <p className="inline-block rounded-full bg-slate-900 px-3 py-1 text-xs font-semibold uppercase tracking-[0.22em] text-slate-50">
            Nexus MENA OSINT
          </p>
          <h1 className="mt-4 max-w-4xl text-3xl font-semibold leading-tight md:text-5xl">
            Multidomain Disinformation & Risk Monitoring Platform
          </h1>
          <p className="mt-4 max-w-3xl text-sm text-slate-600 md:text-base">
            Real-time case intelligence across X, Telegram, YouTube, Instagram, and web infrastructure with
            evidence-first workflows and explainable risk scoring.
          </p>
        </header>

        <section className="grid gap-4 md:grid-cols-3">
          <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <p className="text-xs uppercase tracking-widest text-slate-500">Average Risk</p>
            <p className="mt-3 text-3xl font-semibold">{metrics.avgRisk}</p>
          </div>
          <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <p className="text-xs uppercase tracking-widest text-slate-500">High Severity Cases</p>
            <p className="mt-3 text-3xl font-semibold">{metrics.r3r4}</p>
          </div>
          <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <p className="text-xs uppercase tracking-widest text-slate-500">Collected Items</p>
            <p className="mt-3 text-3xl font-semibold">{metrics.totalItems}</p>
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
                onClick={handleCreateCase}
                className="w-full rounded-xl bg-slate-900 px-4 py-2 text-sm font-semibold text-white transition hover:bg-slate-700 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {loading ? "Working..." : "Create Case"}
              </button>
              {error ? <p className="text-xs text-rose-700">{error}</p> : null}
            </div>
          </div>

          <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-semibold">Investigation Board</h2>
              <button
                onClick={() => void refresh()}
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
                cases.map((item) => (
                  <article
                    key={item.id}
                    className={`rounded-xl border p-4 transition ${
                      activeCaseId === item.id ? "border-slate-900" : "border-slate-200"
                    }`}
                  >
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <button
                        onClick={() => setActiveCaseId(item.id)}
                        className="text-left text-sm font-semibold text-slate-900"
                      >
                        {item.title}
                      </button>
                      <span
                        className={`rounded-full px-2 py-1 text-xs font-semibold ${SEVERITY_STYLES[item.severity]}`}
                      >
                        {item.severity}
                      </span>
                    </div>
                    <p className="mt-2 text-xs text-slate-600">{item.query}</p>
                    <div className="mt-3 flex flex-wrap gap-2 text-xs text-slate-600">
                      <span>Items: {item.item_count}</span>
                      <span>Risk: {item.risk_score}</span>
                      <span>Status: {item.status}</span>
                    </div>
                    <div className="mt-3 flex flex-wrap gap-2">
                      <button
                        onClick={() => void handleCollect(item.id)}
                        disabled={loading}
                        className="rounded-lg border border-slate-300 px-3 py-1 text-xs font-semibold"
                      >
                        Collect
                      </button>
                      <button
                        onClick={() => void handleAnalyze(item.id)}
                        disabled={loading || item.item_count === 0}
                        className="rounded-lg bg-slate-900 px-3 py-1 text-xs font-semibold text-white disabled:opacity-50"
                      >
                        Analyze
                      </button>
                    </div>
                  </article>
                ))
              )}
            </div>
          </div>
        </section>

        <section className="grid gap-6 xl:grid-cols-[1.25fr_1fr]">
          <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <h2 className="text-xl font-semibold">Graph Snapshot</h2>
            <p className="mt-1 text-sm text-slate-500">Entity and platform links for the active case.</p>
            <div className="mt-4 grid gap-3 md:grid-cols-2">
              <div>
                <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-500">Nodes</h3>
                <ul className="mt-2 max-h-56 space-y-1 overflow-auto text-sm">
                  {(graph?.nodes ?? []).slice(0, 16).map((node) => (
                    <li key={node.id} className="rounded-md bg-slate-100 px-2 py-1">
                      {node.label} <span className="text-xs text-slate-500">({node.type})</span>
                    </li>
                  ))}
                </ul>
              </div>
              <div>
                <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-500">Edges</h3>
                <ul className="mt-2 max-h-56 space-y-1 overflow-auto text-sm">
                  {(graph?.edges ?? []).slice(0, 16).map((edge, index) => (
                    <li key={`${edge.source}-${edge.target}-${index}`} className="rounded-md bg-slate-100 px-2 py-1">
                      {edge.source} → {edge.target}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>

          <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <h2 className="text-xl font-semibold">Risk Policy</h2>
            <div className="mt-4 space-y-3 text-sm text-slate-700">
              <p>
                <strong>Balanced model:</strong> Risk combines harm, coordination, velocity, reach,
                cross-platform spread, and credibility gap.
              </p>
              <p>
                <strong>Escalation:</strong> R3 and R4 cases require analyst validation before external actions.
              </p>
              <p>
                <strong>Evidence-first:</strong> Every case update is tied to observable items and graph links.
              </p>
              <p>
                <strong>Languages:</strong> Arabic + English with narrative linking across mixed-language posts.
              </p>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
