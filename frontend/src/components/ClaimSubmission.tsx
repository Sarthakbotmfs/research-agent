import React, { useState } from "react";
import { ArrowRight, ChevronDown, ChevronUp, Database, Sparkles, Sliders } from "lucide-react";
import type { ClaimSubmissionForm } from "../types/research";
import { ClaimSubmissionSchema } from "../types/research";

interface ClaimSubmissionProps {
  onSubmit: (data: ClaimSubmissionForm) => void;
  isLoading: boolean;
}

const EXAMPLE_CLAIMS = [
  "AI coding assistants improve software developer productivity.",
  "Microservices architecture increases operational failure rates compared to modular monoliths.",
  "Test-driven development significantly reduces defect density in production software.",
  "Open source software maintenance suffers severe sustainability risks due to contributor burnout.",
];

export const ClaimSubmission: React.FC<ClaimSubmissionProps> = ({ onSubmit, isLoading }) => {
  const [claim, setClaim] = useState("");
  const [maxRounds, setMaxRounds] = useState(3);
  const [maxQueries, setMaxQueries] = useState(15);
  const [maxSources, setMaxSources] = useState(40);
  const [allowFullText, setAllowFullText] = useState(true);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [validationError, setValidationError] = useState<string | null>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setValidationError(null);

    const result = ClaimSubmissionSchema.safeParse({
      claim,
      max_rounds: maxRounds,
      max_queries: maxQueries,
      max_sources: maxSources,
      allow_full_text_fetch: allowFullText,
    });

    if (!result.success) {
      setValidationError(result.error.issues[0]?.message || "Validation failed");
      return;
    }

    onSubmit(result.data);
  };

  return (
    <div className="max-w-3xl mx-auto py-10 px-4">
      <div className="text-center mb-8">
        <div className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-sky-500/10 border border-sky-500/20 text-sky-400 text-xs font-medium mb-3">
          <Sparkles className="w-3.5 h-3.5" />
          <span>Local-First Scholarly Discovery</span>
        </div>
        <h1 className="text-3xl font-semibold text-slate-100 tracking-tight mb-2.5">
          Investigate a Scientific or Technical Claim
        </h1>
        <p className="text-sm text-slate-400 max-w-xl mx-auto">
          Autonomous literature discovery across OpenAlex and Crossref. Extracts verified passages, identifies opposing evidence, and synthesizes a traceable report.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="bg-[#101622] rounded-xl border border-slate-800 p-4 shadow-xl focus-within:border-sky-500/50 transition-colors">
          <label htmlFor="claim-input" className="block text-xs font-medium text-slate-400 mb-2">
            RESEARCH CLAIM TO EVALUATE
          </label>
          <textarea
            id="claim-input"
            rows={4}
            value={claim}
            onChange={(e) => {
              setClaim(e.target.value);
              if (validationError) setValidationError(null);
            }}
            placeholder="e.g. AI coding assistants improve software developer productivity."
            className="w-full bg-transparent text-slate-100 text-base placeholder-slate-500 focus:outline-none resize-none leading-relaxed"
            disabled={isLoading}
          />

          <div className="mt-3 pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
            <span className="font-mono text-[11px]">{claim.length} / 1000 characters</span>
            <button
              type="button"
              onClick={() => setShowAdvanced(!showAdvanced)}
              className="flex items-center space-x-1 text-slate-400 hover:text-slate-200 transition-colors"
            >
              <Sliders className="w-3.5 h-3.5" />
              <span>Limits & Scope</span>
              {showAdvanced ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
            </button>
          </div>
        </div>

        {validationError && (
          <div className="p-3 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs">
            {validationError}
          </div>
        )}

        {showAdvanced && (
          <div className="bg-[#101622]/80 border border-slate-800/80 rounded-xl p-5 space-y-4 text-xs">
            <div className="font-medium text-slate-200 flex items-center space-x-2 border-b border-slate-800 pb-2">
              <Database className="w-4 h-4 text-sky-400" />
              <span>Execution Limits & Retrieval Budget</span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="text-slate-400 block mb-1">
                  Research Rounds: <span className="font-mono text-slate-200">{maxRounds}</span>
                </label>
                <input
                  type="range"
                  min={1}
                  max={5}
                  value={maxRounds}
                  onChange={(e) => setMaxRounds(Number(e.target.value))}
                  className="w-full accent-sky-500 cursor-pointer"
                />
                <span className="text-[10px] text-slate-500">Includes counter-evidence loops</span>
              </div>

              <div>
                <label className="text-slate-400 block mb-1">
                  Max Queries: <span className="font-mono text-slate-200">{maxQueries}</span>
                </label>
                <input
                  type="range"
                  min={5}
                  max={30}
                  step={5}
                  value={maxQueries}
                  onChange={(e) => setMaxQueries(Number(e.target.value))}
                  className="w-full accent-sky-500 cursor-pointer"
                />
                <span className="text-[10px] text-slate-500">Bounded API calls across indices</span>
              </div>

              <div>
                <label className="text-slate-400 block mb-1">
                  Max Sources: <span className="font-mono text-slate-200">{maxSources}</span>
                </label>
                <input
                  type="range"
                  min={10}
                  max={100}
                  step={10}
                  value={maxSources}
                  onChange={(e) => setMaxSources(Number(e.target.value))}
                  className="w-full accent-sky-500 cursor-pointer"
                />
                <span className="text-[10px] text-slate-500">Deduplicated unique records</span>
              </div>
            </div>

            <div className="pt-2 flex items-center justify-between border-t border-slate-800/60">
              <span className="text-slate-300">Allow Open Access Full-Text Web Extraction</span>
              <input
                type="checkbox"
                checked={allowFullText}
                onChange={(e) => setAllowFullText(e.target.checked)}
                className="w-4 h-4 rounded border-slate-700 bg-slate-800 text-sky-500 focus:ring-0 cursor-pointer"
              />
            </div>
          </div>
        )}

        <div className="flex items-center justify-between pt-2">
          <div className="text-xs text-slate-500 flex items-center space-x-2">
            <span>Indices:</span>
            <span className="px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 font-mono text-[10px]">OpenAlex</span>
            <span className="px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 font-mono text-[10px]">Crossref</span>
          </div>

          <button
            type="submit"
            disabled={isLoading || claim.trim().length < 10}
            className="flex items-center space-x-2 px-5 py-2.5 rounded-lg bg-sky-600 hover:bg-sky-500 disabled:bg-slate-800 disabled:text-slate-500 text-white font-medium text-sm transition-all shadow-md disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <>
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                <span>Initializing Investigation...</span>
              </>
            ) : (
              <>
                <span>Launch Investigation</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </div>
      </form>

      <div className="mt-10">
        <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">
          Example Research Hypotheses
        </p>
        <div className="grid grid-cols-1 gap-2">
          {EXAMPLE_CLAIMS.map((ex, i) => (
            <button
              key={i}
              type="button"
              onClick={() => {
                setClaim(ex);
                if (validationError) setValidationError(null);
              }}
              className="text-left text-xs p-3 rounded-lg bg-[#101622]/60 hover:bg-[#161e2e] border border-slate-800/80 hover:border-slate-700 text-slate-300 transition-colors"
            >
              "{ex}"
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
