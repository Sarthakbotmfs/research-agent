import React, { useEffect, useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import {
  fetchRecentTasks,
  fetchTaskDetail,
  fetchTaskEvidence,
  fetchTaskReport,
  submitResearchClaim,
  subscribeToTaskEvents,
} from "./api/client";
import { ClaimSubmission } from "./components/ClaimSubmission";
import { FindingsDashboard } from "./components/FindingsDashboard";
import { HistorySidebar } from "./components/HistorySidebar";
import { LiveInvestigation } from "./components/LiveInvestigation";
import { Navbar } from "./components/Navbar";
import { ReportViewer } from "./components/ReportViewer";
import { SourceDetailModal } from "./components/SourceDetailModal";
import type { ClaimSubmissionForm, ResearchEvent, Source, Task } from "./types/research";

type ViewState = "submit" | "investigation" | "dashboard" | "report";

export const App: React.FC = () => {
  const queryClient = useQueryClient();
  const [currentView, setCurrentView] = useState<ViewState>("submit");
  const [activeTaskId, setActiveTaskId] = useState<string | null>(null);
  const [selectedSource, setSelectedSource] = useState<Source | null>(null);
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);
  const [events, setEvents] = useState<ResearchEvent[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Load history list
  const {
    data: historyTasks = [],
    isLoading: isLoadingHistory,
    refetch: refetchHistory,
  } = useQuery({
    queryKey: ["tasks"],
    queryFn: fetchRecentTasks,
  });

  // Load active task details
  const { data: activeTask } = useQuery({
    queryKey: ["task", activeTaskId],
    queryFn: () => (activeTaskId ? fetchTaskDetail(activeTaskId) : null),
    enabled: Boolean(activeTaskId),
    refetchInterval: (query) => {
      const t = query.state.data as Task | undefined;
      return t && ["pending", "planning", "searching", "extracting", "classifying", "verifying", "synthesizing"].includes(t.status)
        ? 2000
        : false;
    },
  });

  // Load evidence for active task
  const { data: evidenceData } = useQuery({
    queryKey: ["evidence", activeTaskId],
    queryFn: () => (activeTaskId ? fetchTaskEvidence(activeTaskId) : null),
    enabled: Boolean(activeTaskId),
  });

  // Load report for active task
  const { data: reportData } = useQuery({
    queryKey: ["report", activeTaskId],
    queryFn: () => (activeTaskId ? fetchTaskReport(activeTaskId) : null),
    enabled: Boolean(activeTaskId && activeTask?.has_report),
  });

  // Subscribe to SSE when active task is ongoing
  useEffect(() => {
    if (!activeTaskId) return;

    const unsubscribe = subscribeToTaskEvents(
      activeTaskId,
      (newEvent) => {
        setEvents((prev) => {
          if (prev.some((e) => e.seq === newEvent.seq)) return prev;
          return [...prev, newEvent];
        });
        // Invalidate task queries on key events
        if (
          ["subclaims_created", "sources_discovered", "evidence_extracted", "task_completed"].includes(
            newEvent.event_type
          )
        ) {
          queryClient.invalidateQueries({ queryKey: ["task", activeTaskId] });
          queryClient.invalidateQueries({ queryKey: ["evidence", activeTaskId] });
        }
      },
      () => {
        queryClient.invalidateQueries({ queryKey: ["task", activeTaskId] });
        queryClient.invalidateQueries({ queryKey: ["evidence", activeTaskId] });
        queryClient.invalidateQueries({ queryKey: ["report", activeTaskId] });
        queryClient.invalidateQueries({ queryKey: ["tasks"] });
      }
    );

    return () => {
      unsubscribe();
    };
  }, [activeTaskId, queryClient]);

  const handleLaunchClaim = async (formData: ClaimSubmissionForm) => {
    setIsSubmitting(true);
    try {
      const created = await submitResearchClaim(formData);
      setActiveTaskId(created.id);
      setEvents([]);
      setCurrentView("investigation");
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
    } catch (err: any) {
      alert(`Error launching research: ${err.message}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSelectTaskFromHistory = (taskId: string) => {
    setActiveTaskId(taskId);
    setEvents([]);
    // If task is completed, jump directly to findings dashboard
    const t = historyTasks.find((item) => item.id === taskId);
    if (t && ["completed", "partial"].includes(t.status)) {
      setCurrentView("dashboard");
    } else {
      setCurrentView("investigation");
    }
  };

  return (
    <div className="min-h-screen bg-[#0b0f17] text-slate-200 flex flex-col font-sans">
      <Navbar
        onNewResearch={() => {
          setCurrentView("submit");
        }}
        onToggleHistory={() => setIsHistoryOpen(true)}
        activeTaskId={activeTaskId}
      />

      <main className="flex-1 pb-16">
        {currentView === "submit" && (
          <ClaimSubmission onSubmit={handleLaunchClaim} isLoading={isSubmitting} />
        )}

        {currentView === "investigation" && activeTask && (
          <LiveInvestigation
            task={activeTask}
            events={events}
            onViewDashboard={() => setCurrentView("dashboard")}
            onViewReport={() => setCurrentView("report")}
          />
        )}

        {currentView === "dashboard" && activeTask && (
          <FindingsDashboard
            task={activeTask}
            evidenceItems={evidenceData?.items || []}
            onSelectSource={(source) => setSelectedSource(source)}
            onViewReport={() => setCurrentView("report")}
          />
        )}

        {currentView === "report" && activeTask && reportData && (
          <ReportViewer
            task={activeTask}
            report={reportData}
            onBackToDashboard={() => setCurrentView("dashboard")}
            onSelectSource={(source) => setSelectedSource(source)}
          />
        )}
      </main>

      {/* Source Detail Modal */}
      <SourceDetailModal
        source={selectedSource}
        onClose={() => setSelectedSource(null)}
      />

      {/* History Sidebar */}
      <HistorySidebar
        isOpen={isHistoryOpen}
        onClose={() => setIsHistoryOpen(false)}
        tasks={historyTasks}
        activeTaskId={activeTaskId}
        onSelectTask={handleSelectTaskFromHistory}
        onRefresh={() => refetchHistory()}
        isLoading={isLoadingHistory}
      />
    </div>
  );
};
