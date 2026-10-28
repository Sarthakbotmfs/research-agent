import React from "react";
import { BookOpen, History, PlusCircle, ShieldCheck } from "lucide-react";

interface NavbarProps {
  onNewResearch: () => void;
  onToggleHistory: () => void;
  activeTaskId: string | null;
}

export const Navbar: React.FC<NavbarProps> = ({
  onNewResearch,
  onToggleHistory,
  activeTaskId,
}) => {
  return (
    <header className="border-b border-slate-800 bg-[#101622]/90 backdrop-blur sticky top-0 z-40 px-6 py-3.5">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <div className="flex items-center space-x-3 cursor-pointer" onClick={onNewResearch}>
          <div className="p-2 rounded-lg bg-sky-500/10 border border-sky-500/30 text-sky-400">
            <BookOpen className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-semibold text-slate-100 text-base tracking-tight">Research Agent</span>
              <span className="text-[10px] font-mono uppercase bg-slate-800 text-slate-400 px-1.5 py-0.5 rounded border border-slate-700">
                Phase 1
              </span>
              {activeTaskId && (
                <span className="text-[10px] font-mono text-sky-400 bg-sky-950/40 px-1.5 py-0.5 rounded border border-sky-800/40 hidden sm:inline">
                  Task: {activeTaskId.slice(0, 8)}
                </span>
              )}
            </div>
            <p className="text-xs text-slate-400 flex items-center space-x-1">
              <ShieldCheck className="w-3 h-3 text-emerald-400 inline" />
              <span>Evidence-Grounded Scholarly Verification</span>
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={onToggleHistory}
            className="flex items-center space-x-2 text-xs font-medium px-3 py-2 rounded-md bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700 text-slate-300 transition-colors"
          >
            <History className="w-3.5 h-3.5 text-slate-400" />
            <span>History</span>
          </button>

          <button
            onClick={onNewResearch}
            className="flex items-center space-x-2 text-xs font-medium px-3.5 py-2 rounded-md bg-sky-600 hover:bg-sky-500 text-white transition-colors shadow-sm"
          >
            <PlusCircle className="w-3.5 h-3.5" />
            <span>New Investigation</span>
          </button>
        </div>
      </div>
    </header>
  );
};
