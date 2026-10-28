import React, { useEffect, useRef, useState } from "react";
import {
  ArrowRight,
  CheckCircle2,
  Compass,
  FileSearch,
  Filter,
  Layers,
  ListTree,
  Loader2,
  Search,
  ShieldCheck,
} from "lucide-react";
import type { ResearchEvent, Task } from "../types/research";

interface LiveInvestigationProps {
  task: Task;
  events: ResearchEvent[];
  onViewDashboard: () => void;
  onViewReport: () => void;
}

const STAGES = [
  { key: "planning", label: "Decomposition & Planning", icon: ListTree },
  { key: "searching", label: "Scholarly Discovery", icon: Search },
  { key: "extracting", label: "Passage Extraction", icon: FileSearch },
  { key: "classifying", label: "Evidence Classification", icon: Filter },
  { key: "verifying", label: "Source & Claim Verification", icon: ShieldCheck },
  { key: "synthesizing", label: "Report Synthesis", icon: Layers },
];

export const LiveInvestigation: React.FC<LiveInvestigationProps> = ({
  task,
  events,
  onViewDashboard,
  onViewReport,
}) => {
  const scrollRef = useRef<HTMLDivElement>(null);
  const [autoScroll, setAutoScroll] = useState(true);

  useEffect(() => {
    if (autoScroll && scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [events, autoScroll]);

  const isTerminal = ["completed", "partial", "failed"].includes(task.status);
  const currentStageIndex = STAGES.findIndex((s) => s.key === task.status);

  // Derive actual metrics from events
  const queriesExecuted = events.filter((e) => e.event_type === "query_executed").length;
  const sourcesFound = task.sources_count || 0;
  const evidenceExtracted = task.evidence_count || 0;

  return (
    <div className="max-w-5xl mx-auto py-8 px-4 space-y-6">
      {/* Header Info */}
      <div className="bg-[#101622] rounded-xl border border-slate-800 p-6 shadow-lg">
        <div className="flex items-start justify-between">
          <div className="space-y-2">
            <div className="flex items-center space-x-2">
              <span className="text-[11px] font-mono uppercase px-2 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700">
                TASK ID: {task.id.slice(0, 12)}
              </span>
              <span
                className={`text-[11px] font-mono uppercase px-2 py-0.5 rounded border ${
                  task.status === "completed"
                    ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-400"
                    : task.status === "failed"
                    ? "bg-rose-500/10 border-rose-500/30 text-rose-400"
                    : "bg-sky-500/10 border-sky-500/30 text-sky-400 animate-pulse"
                }`}
              >
                {task.status.toUpperCase()}
              </span>
            </div>
            <h2 className="text-xl font-medium text-slate-100 leading-snug">
              "{task.claim}"
            </h2>
          </div>

          {isTerminal && (
            <div className="flex items-center space-x-2">
              <button
                onClick={onViewDashboard}
                className="px-3.5 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium border border-slate-700 transition-colors"
              >
                View Findings Dashboard
              </button>
              {task.has_report && (
                <button
                  onClick={onViewReport}
                  className="flex items-center space-x-1.5 px-3.5 py-2 rounded-lg bg-sky-600 hover:bg-sky-500 text-white text-xs font-medium transition-colors"
                >
                  <span>Read Report</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              )}
            </div>
          )}
        </div>

        {/* Real Metrics Counter Strip */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-6 pt-5 border-t border-slate-800/80">
          <div className="bg-[#0b0f17] p-3 rounded-lg border border-slate-800/80">
            <span className="text-[11px] text-slate-400 block mb-0.5">Active Stage</span>
            <span className="text-sm font-medium text-slate-200 capitalize flex items-center space-x-1.5">
              {!isTerminal && <Loader2 className="w-3.5 h-3.5 text-sky-400 animate-spin" />}
              <span>{task.status}</span>
            </span>
          </div>

          <div className="bg-[#0b0f17] p-3 rounded-lg border border-slate-800/80">
            <span className="text-[11px] text-slate-400 block mb-0.5">Queries Formulated</span>
            <span className="text-sm font-mono text-slate-200">
              {queriesExecuted} <span className="text-xs text-slate-500">/ {task.config?.max_queries || 15}</span>
            </span>
          </div>

          <div className="bg-[#0b0f17] p-3 rounded-lg border border-slate-800/80">
            <span className="text-[11px] text-slate-400 block mb-0.5">Unique Sources</span>
            <span className="text-sm font-mono text-slate-200">
              {sourcesFound} <span className="text-xs text-slate-500">/ {task.config?.max_sources || 40}</span>
            </span>
          </div>

          <div className="bg-[#0b0f17] p-3 rounded-lg border border-slate-800/80">
            <span className="text-[11px] text-slate-400 block mb-0.5">Evidence Items</span>
            <span className="text-sm font-mono text-emerald-400 font-medium">
              {evidenceExtracted} extracted
            </span>
          </div>
        </div>
      </div>

      {/* Stage Progression Timeline */}
      <div className="bg-[#101622] rounded-xl border border-slate-800 p-5 shadow-lg">
        <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-4">
          Autonomous Investigation Workflow
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-6 gap-2">
          {STAGES.map((s, idx) => {
            const Icon = s.icon;
            const isCompleted = isTerminal || (currentStageIndex > -1 && idx < currentStageIndex);
            const isCurrent = task.status === s.key;

            return (
              <div
                key={s.key}
                className={`p-3 rounded-lg border text-xs flex flex-col justify-between transition-colors ${
                  isCurrent
                    ? "bg-sky-500/10 border-sky-500/40 text-sky-300 ring-1 ring-sky-500/20"
                    : isCompleted
                    ? "bg-[#0b0f17] border-slate-800 text-slate-300"
                    : "bg-[#0b0f17]/50 border-slate-800/50 text-slate-500"
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <Icon className={`w-4 h-4 ${isCurrent ? "text-sky-400" : isCompleted ? "text-emerald-400" : "text-slate-600"}`} />
                  {isCompleted ? (
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                  ) : isCurrent ? (
                    <Loader2 className="w-3.5 h-3.5 text-sky-400 animate-spin" />
                  ) : (
                    <span className="text-[10px] font-mono text-slate-600">0{idx + 1}</span>
                  )}
                </div>
                <span className="font-medium text-[11px] leading-tight">{s.label}</span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Live Event Stream */}
      <div className="bg-[#101622] rounded-xl border border-slate-800 overflow-hidden shadow-lg">
        <div className="px-5 py-3.5 border-b border-slate-800 flex items-center justify-between bg-[#131b2a]">
          <div className="flex items-center space-x-2">
            <Compass className="w-4 h-4 text-sky-400" />
            <span className="text-xs font-semibold text-slate-200">Investigation Event Log</span>
            <span className="text-[11px] font-mono text-slate-500">({events.length} events)</span>
          </div>

          <div className="flex items-center space-x-3 text-xs">
            <label className="flex items-center space-x-1.5 text-slate-400 cursor-pointer">
              <input
                type="checkbox"
                checked={autoScroll}
                onChange={(e) => setAutoScroll(e.target.checked)}
                className="rounded border-slate-700 bg-slate-800 text-sky-500 w-3.5 h-3.5"
              />
              <span className="text-[11px]">Auto-scroll</span>
            </label>
          </div>
        </div>

        <div
          ref={scrollRef}
          className="p-4 max-h-[380px] overflow-y-auto space-y-2 font-mono text-xs bg-[#0b0f17]"
        >
          {events.length === 0 ? (
            <div className="text-center py-10 text-slate-500 text-xs font-sans">
              Connecting to real-time event stream...
            </div>
          ) : (
            events.map((ev) => (
              <div
                key={ev.id || ev.seq}
                className="p-2.5 rounded bg-[#101622] border border-slate-800/80 flex items-start space-x-3 text-[11px]"
              >
                <span className="text-slate-500 font-mono text-[10px] shrink-0 pt-0.5">
                  #{ev.seq}
                </span>

                <span
                  className={`px-1.5 py-0.5 rounded text-[10px] uppercase font-mono font-medium shrink-0 ${
                    ev.stage === "searching"
                      ? "bg-blue-500/10 text-blue-400 border border-blue-500/20"
                      : ev.stage === "classifying"
                      ? "bg-purple-500/10 text-purple-400 border border-purple-500/20"
                      : ev.stage === "gap_analysis"
                      ? "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                      : ev.stage === "verifying"
                      ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                      : "bg-slate-800 text-slate-300"
                  }`}
                >
                  {ev.stage}
                </span>

                <div className="flex-1 text-slate-300 leading-relaxed font-sans">
                  {ev.message}
                  {ev.data && ev.data.query && (
                    <span className="block mt-1 font-mono text-[10px] text-sky-400 bg-sky-950/40 px-2 py-0.5 rounded border border-sky-800/30">
                      Query: "{ev.data.query}"
                    </span>
                  )}
                  {ev.data && ev.data.counter_queries && (
                    <div className="mt-1 space-y-0.5">
                      {ev.data.counter_queries.map((cq: string, i: number) => (
                        <span key={i} className="block font-mono text-[10px] text-amber-400 bg-amber-950/40 px-2 py-0.5 rounded border border-amber-800/30">
                          Counter-Query: "{cq}"
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                <span className="text-[10px] text-slate-500 shrink-0 font-mono">
                  {new Date(ev.created_at).toLocaleTimeString([], { hour12: false })}
                </span>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};
