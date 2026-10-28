import React, { useState } from "react";
import {
  CheckCircle2,
  FileText,
  Filter,
  HelpCircle,
  Scale,
  Search,
  XCircle,
} from "lucide-react";
import type { EvidenceItem, Source, Task } from "../types/research";
import { EvidenceCard } from "./EvidenceCard";

interface FindingsDashboardProps {
  task: Task;
  evidenceItems: EvidenceItem[];
  onSelectSource: (source: Source) => void;
  onViewReport: () => void;
}

type TabCategory = "supporting" | "contradicting" | "common_ground" | "insufficient";

export const FindingsDashboard: React.FC<FindingsDashboardProps> = ({
  task,
  evidenceItems,
  onSelectSource,
  onViewReport,
}) => {
  const [activeTab, setActiveTab] = useState<TabCategory>("supporting");
  const [aspectFilter, setAspectFilter] = useState<string>("all");
  const [searchQuery, setSearchQuery] = useState("");

  // Categorize items
  const supporting = evidenceItems.filter((e) => e.relationship === "supports");
  const contradicting = evidenceItems.filter((e) => e.relationship === "contradicts");
  const commonGround = evidenceItems.filter((e) => e.relationship === "mixed" || e.relationship === "context");
  const insufficient = evidenceItems.filter((e) => e.relationship === "insufficient");

  // Get active items by tab
  const getActiveList = () => {
    switch (activeTab) {
      case "supporting":
        return supporting;
      case "contradicting":
        return contradicting;
      case "common_ground":
        return commonGround;
      case "insufficient":
        return insufficient;
    }
  };

  // Unique aspects for filter dropdown
  const aspects = Array.from(
    new Set(evidenceItems.map((e) => e.subclaim?.aspect).filter(Boolean))
  ) as string[];

  // Filter active items
  const filteredItems = getActiveList().filter((item) => {
    if (aspectFilter !== "all" && item.subclaim?.aspect !== aspectFilter) {
      return false;
    }
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      const inPassage = item.passage.toLowerCase().includes(q);
      const inTitle = item.source?.title.toLowerCase().includes(q) || false;
      const inRationale = item.rationale.toLowerCase().includes(q);
      return inPassage || inTitle || inRationale;
    }
    return true;
  });

  return (
    <div className="max-w-6xl mx-auto py-8 px-4 space-y-6">
      {/* Header and Summary Bar */}
      <div className="bg-[#101622] rounded-xl border border-slate-800 p-6 shadow-lg">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-5">
          <div>
            <div className="flex items-center space-x-2 mb-1.5">
              <span className="text-[11px] font-mono uppercase px-2 py-0.5 rounded bg-sky-500/10 border border-sky-500/30 text-sky-400">
                FINDINGS DASHBOARD
              </span>
              <span className="text-xs text-slate-500 font-mono">
                {evidenceItems.length} Evidence Passages Extracted
              </span>
            </div>
            <h2 className="text-lg font-semibold text-slate-100 leading-snug">
              "{task.claim}"
            </h2>
          </div>

          {task.has_report && (
            <button
              onClick={onViewReport}
              className="flex items-center space-x-2 px-4 py-2 rounded-lg bg-sky-600 hover:bg-sky-500 text-white font-medium text-xs transition-colors shrink-0 shadow-sm"
            >
              <FileText className="w-3.5 h-3.5" />
              <span>Full Synthesis Report</span>
            </button>
          )}
        </div>

        {/* 4 Category Tabs */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-5">
          <button
            onClick={() => setActiveTab("supporting")}
            className={`p-3.5 rounded-lg border text-left transition-all ${
              activeTab === "supporting"
                ? "bg-emerald-500/10 border-emerald-500/50 ring-1 ring-emerald-500/20 text-emerald-300"
                : "bg-[#0b0f17] border-slate-800 hover:border-slate-700 text-slate-400"
            }`}
          >
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs font-semibold">Supporting</span>
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            </div>
            <div className="text-2xl font-mono font-bold text-slate-100">{supporting.length}</div>
            <span className="text-[10px] text-slate-500">Direct empirical confirmation</span>
          </button>

          <button
            onClick={() => setActiveTab("contradicting")}
            className={`p-3.5 rounded-lg border text-left transition-all ${
              activeTab === "contradicting"
                ? "bg-rose-500/10 border-rose-500/50 ring-1 ring-rose-500/20 text-rose-300"
                : "bg-[#0b0f17] border-slate-800 hover:border-slate-700 text-slate-400"
            }`}
          >
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs font-semibold">Contradicting</span>
              <XCircle className="w-4 h-4 text-rose-400" />
            </div>
            <div className="text-2xl font-mono font-bold text-slate-100">{contradicting.length}</div>
            <span className="text-[10px] text-slate-500">Refutations & counter-evidence</span>
          </button>

          <button
            onClick={() => setActiveTab("common_ground")}
            className={`p-3.5 rounded-lg border text-left transition-all ${
              activeTab === "common_ground"
                ? "bg-amber-500/10 border-amber-500/50 ring-1 ring-amber-500/20 text-amber-300"
                : "bg-[#0b0f17] border-slate-800 hover:border-slate-700 text-slate-400"
            }`}
          >
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs font-semibold">Common Ground</span>
              <Scale className="w-4 h-4 text-amber-400" />
            </div>
            <div className="text-2xl font-mono font-bold text-slate-100">{commonGround.length}</div>
            <span className="text-[10px] text-slate-500">Nuanced tradeoffs & context</span>
          </button>

          <button
            onClick={() => setActiveTab("insufficient")}
            className={`p-3.5 rounded-lg border text-left transition-all ${
              activeTab === "insufficient"
                ? "bg-slate-700/30 border-slate-600/50 ring-1 ring-slate-600/20 text-slate-200"
                : "bg-[#0b0f17] border-slate-800 hover:border-slate-700 text-slate-400"
            }`}
          >
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs font-semibold">Insufficient</span>
              <HelpCircle className="w-4 h-4 text-slate-400" />
            </div>
            <div className="text-2xl font-mono font-bold text-slate-100">{insufficient.length}</div>
            <span className="text-[10px] text-slate-500">Gaps lacking causal data</span>
          </button>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3">
        <div className="relative w-full sm:w-72">
          <Search className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Search passages, titles, authors..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-[#101622] text-xs text-slate-200 pl-9 pr-3 py-2 rounded-lg border border-slate-800 focus:outline-none focus:border-sky-500"
          />
        </div>

        {aspects.length > 0 && (
          <div className="flex items-center space-x-2 text-xs text-slate-400 w-full sm:w-auto">
            <Filter className="w-3.5 h-3.5 text-slate-500" />
            <span>Aspect:</span>
            <select
              value={aspectFilter}
              onChange={(e) => setAspectFilter(e.target.value)}
              className="bg-[#101622] text-xs text-slate-200 px-3 py-1.5 rounded-lg border border-slate-800 focus:outline-none focus:border-sky-500"
            >
              <option value="all">All Aspects ({evidenceItems.length})</option>
              {aspects.map((aspect) => (
                <option key={aspect} value={aspect}>
                  {aspect}
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      {/* Cards Grid */}
      {filteredItems.length === 0 ? (
        <div className="bg-[#101622] rounded-xl border border-slate-800/80 p-12 text-center text-slate-400 text-xs">
          No evidence items found under "{activeTab.replace("_", " ")}" matching the current filters.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filteredItems.map((item) => (
            <EvidenceCard
              key={item.id}
              evidence={item}
              onSelectSource={onSelectSource}
            />
          ))}
        </div>
      )}
    </div>
  );
};
