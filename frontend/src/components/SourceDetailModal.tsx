import React from "react";
import { ExternalLink, X } from "lucide-react";
import type { Source } from "../types/research";

interface SourceDetailModalProps {
  source: Source | null;
  onClose: () => void;
}

export const SourceDetailModal: React.FC<SourceDetailModalProps> = ({ source, onClose }) => {
  if (!source) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
      <div className="bg-[#101622] rounded-xl border border-slate-700 max-w-2xl w-full max-h-[85vh] flex flex-col shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-800 flex items-start justify-between bg-[#131b2a]">
          <div>
            <div className="flex items-center space-x-2 mb-1.5">
              <span className="text-[10px] font-mono uppercase bg-slate-800 text-slate-400 px-2 py-0.5 rounded border border-slate-700">
                PROVENANCE: {source.provenance.toUpperCase()}
              </span>
              {source.is_peer_reviewed && (
                <span className="text-[10px] font-mono uppercase bg-emerald-950/40 border border-emerald-800/40 text-emerald-400 px-2 py-0.5 rounded">
                  Peer-Reviewed
                </span>
              )}
            </div>
            <h3 className="text-base font-semibold text-slate-100 leading-snug">
              {source.title}
            </h3>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-slate-100 hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Scrollable Content */}
        <div className="p-6 overflow-y-auto space-y-5 text-xs text-slate-300">
          {/* Metadata Grid */}
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3 bg-[#0b0f17] p-4 rounded-lg border border-slate-800">
            <div>
              <span className="text-[10px] text-slate-500 uppercase font-mono block">Publication Year</span>
              <span className="text-slate-200 font-mono text-sm">{source.year || "n.d."}</span>
            </div>
            <div>
              <span className="text-[10px] text-slate-500 uppercase font-mono block">Citations</span>
              <span className="text-slate-200 font-mono text-sm">{source.citation_count} cited</span>
            </div>
            <div>
              <span className="text-[10px] text-slate-500 uppercase font-mono block">Open Access</span>
              <span className={`text-sm font-medium ${source.open_access ? "text-emerald-400" : "text-slate-400"}`}>
                {source.open_access ? "Available" : "Restricted"}
              </span>
            </div>
            <div className="col-span-2">
              <span className="text-[10px] text-slate-500 uppercase font-mono block">Venue / Container</span>
              <span className="text-slate-200">{source.venue || "Scholarly Proceedings"}</span>
            </div>
            <div>
              <span className="text-[10px] text-slate-500 uppercase font-mono block">Extraction Status</span>
              <span className="font-mono text-sky-400">{source.extraction_status}</span>
            </div>
          </div>

          {/* Authors */}
          <div>
            <h4 className="font-semibold text-slate-200 mb-1">Authors</h4>
            <div className="flex flex-wrap gap-1.5">
              {source.authors && source.authors.length > 0 ? (
                source.authors.map((author, i) => (
                  <span key={i} className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 text-[11px]">
                    {author}
                  </span>
                ))
              ) : (
                <span className="text-slate-500 italic">No author metadata provided</span>
              )}
            </div>
          </div>

          {/* Abstract */}
          <div>
            <h4 className="font-semibold text-slate-200 mb-1">Abstract</h4>
            <div className="bg-[#0b0f17] p-3 rounded-lg border border-slate-800 text-slate-300 leading-relaxed max-h-52 overflow-y-auto font-sans">
              {source.abstract || "Full abstract not provided in index metadata."}
            </div>
          </div>

          {/* Identifiers */}
          <div className="space-y-1">
            <h4 className="font-semibold text-slate-200 mb-1">Canonical Identifiers & Provenance</h4>
            {source.doi && (
              <div className="flex items-center space-x-2 text-[11px] font-mono text-slate-400">
                <span className="text-slate-500">DOI:</span>
                <span className="text-sky-400 select-all">{source.doi}</span>
              </div>
            )}
            {source.content_hash && (
              <div className="flex items-center space-x-2 text-[11px] font-mono text-slate-400">
                <span className="text-slate-500">SHA-256:</span>
                <span className="text-slate-400 select-all text-[10px]">{source.content_hash}</span>
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-3.5 border-t border-slate-800 bg-[#131b2a] flex items-center justify-between">
          <span className="text-xs text-slate-500">Registry: {source.provenance}</span>
          <a
            href={source.doi ? `https://doi.org/${source.doi}` : source.canonical_url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center space-x-1.5 px-4 py-2 rounded-lg bg-sky-600 hover:bg-sky-500 text-white font-medium text-xs transition-colors shadow-sm"
          >
            <span>Open Publication</span>
            <ExternalLink className="w-3.5 h-3.5" />
          </a>
        </div>
      </div>
    </div>
  );
};
