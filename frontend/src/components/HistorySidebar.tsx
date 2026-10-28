import React from "react";
import { History, RefreshCw, X } from "lucide-react";
import type { Task } from "../types/research";

interface HistorySidebarProps {
  isOpen: boolean;
  onClose: () => void;
  tasks: Task[];
  activeTaskId: string | null;
  onSelectTask: (taskId: string) => void;
  onRefresh: () => void;
  isLoading: boolean;
}

export const HistorySidebar: React.FC<HistorySidebarProps> = ({
  isOpen,
  onClose,
  tasks,
  activeTaskId,
  onSelectTask,
  onRefresh,
  isLoading,
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-black/60 backdrop-blur-xs">
      <div className="w-full max-w-md bg-[#101622] border-l border-slate-800 h-full flex flex-col shadow-2xl">
        {/* Header */}
        <div className="px-5 py-4 border-b border-slate-800 flex items-center justify-between bg-[#131b2a]">
          <div className="flex items-center space-x-2">
            <History className="w-4 h-4 text-sky-400" />
            <h3 className="font-semibold text-slate-100 text-sm">Research History</h3>
            <span className="text-xs font-mono text-slate-500">({tasks.length})</span>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={onRefresh}
              disabled={isLoading}
              className="p-1.5 rounded text-slate-400 hover:text-slate-100 hover:bg-slate-800 transition-colors"
              title="Refresh History"
            >
              <RefreshCw className={`w-4 h-4 ${isLoading ? "animate-spin" : ""}`} />
            </button>
            <button
              onClick={onClose}
              className="p-1.5 rounded text-slate-400 hover:text-slate-100 hover:bg-slate-800 transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Task List */}
        <div className="flex-1 overflow-y-auto p-4 space-y-2.5 text-xs">
          {tasks.length === 0 ? (
            <div className="text-center py-16 text-slate-500">
              No research tasks submitted yet.
            </div>
          ) : (
            tasks.map((task) => {
              const isActive = task.id === activeTaskId;
              return (
                <div
                  key={task.id}
                  onClick={() => {
                    onSelectTask(task.id);
                    onClose();
                  }}
                  className={`p-3.5 rounded-xl border text-left cursor-pointer transition-all ${
                    isActive
                      ? "bg-sky-500/10 border-sky-500/50 ring-1 ring-sky-500/30"
                      : "bg-[#0b0f17] border-slate-800 hover:border-slate-700"
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span
                      className={`text-[10px] font-mono uppercase px-2 py-0.5 rounded border ${
                        task.status === "completed"
                          ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-400"
                          : task.status === "failed"
                          ? "bg-rose-500/10 border-rose-500/30 text-rose-400"
                          : "bg-sky-500/10 border-sky-500/30 text-sky-400 animate-pulse"
                      }`}
                    >
                      {task.status}
                    </span>

                    <span className="text-[10px] text-slate-500 font-mono">
                      {new Date(task.created_at).toLocaleDateString([], {
                        month: "short",
                        day: "numeric",
                        hour: "2-digit",
                        minute: "2-digit",
                      })}
                    </span>
                  </div>

                  <p className="font-medium text-slate-200 line-clamp-2 leading-relaxed mb-2">
                    "{task.claim}"
                  </p>

                  <div className="flex items-center space-x-3 text-[11px] text-slate-400 pt-1 border-t border-slate-800/60 font-mono">
                    <span>{task.sources_count} sources</span>
                    <span>•</span>
                    <span className="text-emerald-400">{task.evidence_count} evidence</span>
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
};
