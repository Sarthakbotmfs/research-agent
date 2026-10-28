import type {
  ClaimSubmissionForm,
  EvidenceListResponse,
  Report,
  ResearchEvent,
  Task,
} from "../types/research";

const API_BASE = "/api";

export async function submitResearchClaim(formData: ClaimSubmissionForm): Promise<Task> {
  const resp = await fetch(`${API_BASE}/research`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      claim: formData.claim,
      config: {
        max_rounds: formData.max_rounds,
        max_queries: formData.max_queries,
        max_sources: formData.max_sources,
        allow_full_text_fetch: formData.allow_full_text_fetch,
      },
    }),
  });

  if (!resp.ok) {
    const err = await resp.json().catch(() => ({ detail: "Failed to submit claim" }));
    throw new Error(err.detail || "Submission failed");
  }

  return resp.json();
}

export async function fetchTaskDetail(taskId: string): Promise<Task> {
  const resp = await fetch(`${API_BASE}/research/${taskId}`);
  if (!resp.ok) {
    throw new Error(`Failed to load research task ${taskId}`);
  }
  return resp.json();
}

export async function fetchRecentTasks(): Promise<Task[]> {
  const resp = await fetch(`${API_BASE}/research?limit=30`);
  if (!resp.ok) {
    throw new Error("Failed to load research history");
  }
  return resp.json();
}

export async function fetchTaskEvidence(taskId: string): Promise<EvidenceListResponse> {
  const resp = await fetch(`${API_BASE}/research/${taskId}/evidence`);
  if (!resp.ok) {
    throw new Error(`Failed to load evidence for task ${taskId}`);
  }
  return resp.json();
}

export async function fetchTaskReport(taskId: string): Promise<Report> {
  const resp = await fetch(`${API_BASE}/research/${taskId}/report`);
  if (!resp.ok) {
    throw new Error(`Failed to load report for task ${taskId}`);
  }
  return resp.json();
}

export function getExportDownloadUrl(taskId: string, format: "md" | "json" | "pdf"): string {
  return `${API_BASE}/research/${taskId}/export?format=${format}`;
}

export function subscribeToTaskEvents(
  taskId: string,
  onEvent: (event: ResearchEvent) => void,
  onDone: (status: string) => void,
  onError?: (err: any) => void,
  afterSeq: number = 0
): () => void {
  const url = `${API_BASE}/research/${taskId}/events?after_seq=${afterSeq}`;
  const eventSource = new EventSource(url);

  const eventTypes = [
    "task_started",
    "stage_started",
    "subclaims_created",
    "round_started",
    "query_executed",
    "sources_discovered",
    "evidence_extracted",
    "counter_queries_generated",
    "verification_completed",
    "task_completed",
    "task_error",
  ];

  for (const type of eventTypes) {
    eventSource.addEventListener(type, (e: MessageEvent) => {
      try {
        const parsed: ResearchEvent = JSON.parse(e.data);
        onEvent(parsed);
      } catch (err) {
        console.error("Error parsing SSE event:", err);
      }
    });
  }

  eventSource.addEventListener("done", (e: MessageEvent) => {
    try {
      const data = JSON.parse(e.data);
      onDone(data.status || "completed");
    } catch {
      onDone("completed");
    }
    eventSource.close();
  });

  eventSource.onerror = (e) => {
    if (onError) onError(e);
  };

  return () => {
    eventSource.close();
  };
}
