import React from "react";
import {
  AlertTriangle,
  CheckCircle,
  ExternalLink,
  HelpCircle,
  Info,
  Scale,
  ShieldCheck,
  XCircle,
} from "lucide-react";
import type { EvidenceItem, Source } from "../types/research";

interface EvidenceCardProps {
  evidence: EvidenceItem;
  onSelectSource?: (source: Source) => void;
}

export const EvidenceCard: React.FC<EvidenceCardProps> = ({ evidence, onSelectSource }) => {
  const { source, subclaim, relationship, passage, rationale, limitations, verification_status } = evidence;

  const getRelationshipBadge = (rel: string) => {
    switch (rel) {
      case "supports":
        return {
          label: "Supports",
          bg: "bg-emerald-500/10 text-emerald-400 border-emerald-500/30",
          icon: CheckCircle,
        };
      case "contradicts":
        return {
          label: "Contradicts",
          bg: "bg-rose-500/10 text-rose-400 border-rose-500/30",
          icon: XCircle,
        };
      case "mixed":
        return {
          label: "Mixed / Tradeoff",
          bg: "bg-amber-500/10 text-amber-400 border-amber-500/30",
          icon: Scale,
        };
      case "context":
        return {
          label: "Context",
          bg: "bg-sky-500/10 text-sky-400 border-sky-500/30",
          icon: Info,
        };
      default:
        return {
          label: "Insufficient Evidence",
          bg: "bg-slate-700/30 text-slate-400 border-slate-600/30",
          icon: HelpCircle,
        };
    }
  };

  const badge = getRelationshipBadge(relationship);
  const BadgeIcon = badge.icon;

  const authorsDisplay = source?.authors && source.authors.length > 0
    ? source.authors.slice(0, 3).join(", ") + (source.authors.length > 3 ? " et al." : "")
    : "Scholarly Authors";

  return (
    <div className="bg-[#101622] rounded-xl border border-slate-800 hover:border-slate-700 p-5 shadow-md transition-all flex flex-col justify-between space-y-4">
      <div className="space-y-3">
        {/* Top Badges */}
        <div className="flex items-center justify-between gap-2 flex-wrap">
          <span className={`inline-flex items-center space-x-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium border ${badge.bg}`}>
            <BadgeIcon className="w-3.5 h-3.5" />
            <span>{badge.label}</span>
          </span>

          <div className="flex items-center space-x-2 text-[11px] text-slate-400">
            {source?.is_peer_reviewed && (
              <span className="px-2 py-0.5 rounded bg-emerald-950/40 border border-emerald-800/40 text-emerald-400 font-mono text-[10px]">
                Peer-Reviewed
              </span>
            )}
            <span className="px-2 py-0.5 rounded bg-slate-800 border border-slate-700 text-slate-300 font-mono text-[10px] uppercase">
              {source?.source_type || "Source"}
            </span>
          </div>
        </div>

        {/* Subclaim Context */}
        {subclaim && (
          <div className="text-xs text-slate-400 bg-[#0b0f17] p-2 rounded border border-slate-800/80">
            <span className="text-[10px] uppercase font-mono text-slate-500 block">Subclaim Aspect: {subclaim.aspect}</span>
            <span className="text-slate-200 line-clamp-2">"{subclaim.subclaim_text}"</span>
          </div>
        )}

        {/* Source Title & Authors */}
        <div>
          <h4
            className="text-sm font-semibold text-slate-100 hover:text-sky-300 cursor-pointer line-clamp-2 transition-colors"
            onClick={() => source && onSelectSource && onSelectSource(source)}
          >
            {source?.title || "Scholarly Paper"}
          </h4>
          <p className="text-xs text-slate-400 mt-1 line-clamp-1">
            {authorsDisplay} {source?.year ? `(${source.year})` : ""}
            {source?.venue ? ` — ${source.venue}` : ""}
          </p>
        </div>

        {/* Quoted Passage Excerpt */}
        <div className="bg-[#0b0f17] rounded-lg p-3 border-l-2 border-sky-500 border-slate-800/80 text-xs text-slate-300 italic leading-relaxed">
          "{passage}"
        </div>

        {/* Rationale & Limitations */}
        <div className="space-y-1.5 text-xs text-slate-300 pt-1">
          <div>
            <span className="font-semibold text-slate-400">Rationale: </span>
            <span className="text-slate-300">{rationale}</span>
          </div>

          {limitations && (
            <div className="flex items-start space-x-1 text-slate-400 bg-amber-500/5 p-2 rounded border border-amber-500/10">
              <AlertTriangle className="w-3.5 h-3.5 text-amber-400 shrink-0 mt-0.5" />
              <span className="text-[11px] leading-tight text-amber-300/90">{limitations}</span>
            </div>
          )}
        </div>
      </div>

      {/* Footer / Links */}
      <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs">
        <div className="flex items-center space-x-2">
          <span className="flex items-center space-x-1 text-[11px] text-emerald-400/90">
            <ShieldCheck className="w-3.5 h-3.5" />
            <span className="capitalize">{verification_status}</span>
          </span>
          {evidence.is_independent && (
            <span className="text-[10px] font-mono text-slate-400 bg-slate-800/80 px-1.5 py-0.5 rounded">
              Independent Study
            </span>
          )}
        </div>

        {source && (
          <div className="flex items-center space-x-3">
            <button
              onClick={() => onSelectSource && onSelectSource(source)}
              className="text-xs text-slate-400 hover:text-slate-200 transition-colors"
            >
              Details
            </button>
            <a
              href={source.doi ? `https://doi.org/${source.doi}` : source.canonical_url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center space-x-1 text-sky-400 hover:text-sky-300 font-medium"
            >
              <span>Source</span>
              <ExternalLink className="w-3 h-3" />
            </a>
          </div>
        )}
      </div>
    </div>
  );
};
