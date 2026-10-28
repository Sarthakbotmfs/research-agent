import React from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import {
  AlertCircle,
  ArrowLeft,
  ExternalLink,
  FileCode,
  FileDown,
  FileText,
  Layers,
  Scale,
  ShieldCheck,
} from "lucide-react";
import { getExportDownloadUrl } from "../api/client";
import type { Report, Source, Task } from "../types/research";

interface ReportViewerProps {
  task: Task;
  report: Report;
  onBackToDashboard: () => void;
  onSelectSource?: (source: Source) => void;
}

export const ReportViewer: React.FC<ReportViewerProps> = ({
  task,
  report,
  onBackToDashboard,
}) => {
  return (
    <div className="max-w-4xl mx-auto py-8 px-4 space-y-6">
      {/* Top Navigation & Export Toolbar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-[#101622] rounded-xl border border-slate-800 p-4 shadow-lg">
        <button
          onClick={onBackToDashboard}
          className="flex items-center space-x-1.5 text-xs text-slate-400 hover:text-slate-100 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Findings Dashboard</span>
        </button>

        <div className="flex items-center space-x-2">
          <span className="text-[11px] text-slate-500 mr-1 hidden sm:inline">Export Report:</span>
          <a
            href={getExportDownloadUrl(task.id, "md")}
            download
            className="flex items-center space-x-1 text-xs px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition-colors"
          >
            <FileDown className="w-3.5 h-3.5 text-sky-400" />
            <span>Markdown</span>
          </a>

          <a
            href={getExportDownloadUrl(task.id, "json")}
            download
            className="flex items-center space-x-1 text-xs px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition-colors"
          >
            <FileCode className="w-3.5 h-3.5 text-amber-400" />
            <span>JSON</span>
          </a>

          <a
            href={getExportDownloadUrl(task.id, "pdf")}
            download
            className="flex items-center space-x-1 text-xs px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition-colors"
          >
            <FileText className="w-3.5 h-3.5 text-rose-400" />
            <span>PDF</span>
          </a>
        </div>
      </div>

      {/* Main Report Document */}
      <article className="bg-[#101622] rounded-xl border border-slate-800 p-8 shadow-xl space-y-8 font-sans">
        {/* Document Header */}
        <header className="border-b border-slate-800 pb-6 space-y-3">
          <div className="flex items-center space-x-2">
            <span className="text-[10px] font-mono uppercase bg-emerald-950/40 border border-emerald-800/40 text-emerald-400 px-2 py-0.5 rounded">
              Status: {report.status.toUpperCase()}
            </span>
            <span className="text-[10px] font-mono text-slate-500">
              Generated {new Date(report.created_at).toLocaleDateString()}
            </span>
          </div>

          <h1 className="text-2xl font-bold text-slate-100 tracking-tight leading-snug">
            {report.title}
          </h1>

          <div className="bg-[#0b0f17] rounded-lg p-3 border border-slate-800 text-xs">
            <span className="text-slate-500 font-mono block mb-1">EVALUATED HYPOTHESIS:</span>
            <span className="text-slate-200 font-medium italic">"{task.claim}"</span>
          </div>
        </header>

        {/* Executive Summary */}
        <section className="space-y-3">
          <h2 className="text-sm font-semibold text-sky-400 uppercase tracking-wider flex items-center space-x-2">
            <ShieldCheck className="w-4 h-4" />
            <span>Executive Summary</span>
          </h2>
          <div className="prose-academic text-slate-200 text-sm leading-relaxed bg-[#0b0f17]/60 p-4 rounded-xl border border-slate-800/80">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {report.executive_summary}
            </ReactMarkdown>
          </div>
        </section>

        {/* Detailed Findings by Subclaim */}
        {report.findings?.subclaim_findings && report.findings.subclaim_findings.length > 0 && (
          <section className="space-y-4">
            <h2 className="text-sm font-semibold text-sky-400 uppercase tracking-wider flex items-center space-x-2">
              <Layers className="w-4 h-4" />
              <span>Subclaim Empirical Findings</span>
            </h2>
            <div className="space-y-3">
              {report.findings.subclaim_findings.map((f: any, i: number) => (
                <div key={i} className="bg-[#0b0f17] p-4 rounded-lg border border-slate-800 space-y-1.5 text-xs">
                  <h3 className="font-semibold text-slate-200 text-sm">
                    {f.subclaim || `Aspect ${i + 1}`}
                  </h3>
                  <p className="text-slate-300 leading-relaxed">{f.summary}</p>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Common Ground & Consensus */}
        {report.common_ground && (
          <section className="space-y-3">
            <h2 className="text-sm font-semibold text-amber-400 uppercase tracking-wider flex items-center space-x-2">
              <Scale className="w-4 h-4" />
              <span>Common Ground & Academic Consensus</span>
            </h2>
            <div className="prose-academic text-slate-300 text-sm leading-relaxed bg-[#0b0f17]/40 p-4 rounded-xl border border-slate-800/80">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {report.common_ground}
              </ReactMarkdown>
            </div>
          </section>
        )}

        {/* Uncertainty and Gaps */}
        {report.uncertainty_and_gaps && (
          <section className="space-y-3">
            <h2 className="text-sm font-semibold text-rose-400 uppercase tracking-wider flex items-center space-x-2">
              <AlertCircle className="w-4 h-4" />
              <span>Uncertainty & Evidence Gaps</span>
            </h2>
            <div className="prose-academic text-slate-300 text-sm leading-relaxed bg-[#0b0f17]/40 p-4 rounded-xl border border-slate-800/80">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {report.uncertainty_and_gaps}
              </ReactMarkdown>
            </div>
          </section>
        )}

        {/* Methodology */}
        {report.methodology && (
          <section className="space-y-3">
            <h2 className="text-sm font-semibold text-slate-400 uppercase tracking-wider">
              Systematic Methodology
            </h2>
            <div className="prose-academic text-slate-400 text-xs leading-relaxed bg-[#0b0f17] p-4 rounded-lg border border-slate-800/80 font-mono">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {report.methodology}
              </ReactMarkdown>
            </div>
          </section>
        )}

        {/* Limitations */}
        {report.limitations && (
          <section className="space-y-3">
            <h2 className="text-sm font-semibold text-slate-400 uppercase tracking-wider">
              Limitations of Automated Synthesis
            </h2>
            <div className="prose-academic text-slate-400 text-xs leading-relaxed bg-[#0b0f17] p-4 rounded-lg border border-slate-800/80">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {report.limitations}
              </ReactMarkdown>
            </div>
          </section>
        )}

        {/* Validated References */}
        <section className="space-y-4 pt-4 border-t border-slate-800">
          <h2 className="text-sm font-semibold text-slate-200 uppercase tracking-wider">
            Validated Scholarly References ({report.citations?.length || 0})
          </h2>
          <div className="space-y-2.5">
            {report.citations && report.citations.length > 0 ? (
              report.citations.map((c, i) => (
                <div
                  key={c.citation_id || i}
                  className="p-3 rounded-lg bg-[#0b0f17] border border-slate-800/80 flex items-start justify-between gap-3 text-xs"
                >
                  <div className="space-y-0.5">
                    <span className="font-mono text-slate-500 mr-2">[{i + 1}]</span>
                    <span className="font-semibold text-slate-200">{c.title}</span>
                    <p className="text-slate-400 text-[11px]">
                      {c.authors && c.authors.length > 0 ? c.authors.join(", ") : "Unknown authors"}{" "}
                      {c.year ? `(${c.year})` : ""} {c.venue ? `— ${c.venue}` : ""}
                    </p>
                  </div>

                  <a
                    href={c.doi ? `https://doi.org/${c.doi}` : c.canonical_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center space-x-1 text-sky-400 hover:text-sky-300 font-mono text-[11px] shrink-0 pt-0.5"
                  >
                    <span>{c.doi ? "DOI" : "URL"}</span>
                    <ExternalLink className="w-3 h-3" />
                  </a>
                </div>
              ))
            ) : (
              <p className="text-xs text-slate-500 italic">No formal citations linked.</p>
            )}
          </div>
        </section>
      </article>
    </div>
  );
};
