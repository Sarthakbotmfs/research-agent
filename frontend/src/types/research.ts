import { z } from "zod";

export type TaskStatus =
  | "pending"
  | "planning"
  | "searching"
  | "extracting"
  | "classifying"
  | "verifying"
  | "synthesizing"
  | "completed"
  | "partial"
  | "failed";

export type EvidenceRelationship =
  | "supports"
  | "contradicts"
  | "mixed"
  | "context"
  | "insufficient";

export interface Subclaim {
  id: string;
  subclaim_text: string;
  aspect: string;
  status: string;
  created_at: string;
}

export interface Source {
  id: string;
  doi?: string | null;
  canonical_url: string;
  title: string;
  authors: string[];
  venue?: string | null;
  year?: number | null;
  source_type: string;
  is_peer_reviewed: boolean;
  provenance: string;
  citation_count: number;
  open_access: boolean;
  abstract?: string | null;
  extraction_status: string;
  content_hash?: string | null;
}

export interface EvidenceItem {
  id: string;
  task_id: string;
  subclaim_id: string;
  source_id: string;
  relationship: EvidenceRelationship;
  passage: string;
  passage_hash: string;
  rationale: string;
  limitations: string;
  confidence_score: number;
  verification_status: string;
  verification_details?: string | null;
  is_independent: boolean;
  created_at: string;
  source?: Source;
  subclaim?: Subclaim;
}

export interface EvidenceListResponse {
  task_id: string;
  total_count: number;
  counts_by_relationship: Record<EvidenceRelationship, number>;
  items: EvidenceItem[];
}

export interface ResearchEvent {
  id: string;
  seq: number;
  task_id: string;
  stage: string;
  event_type: string;
  message: string;
  data: Record<string, any>;
  created_at: string;
}

export interface Citation {
  citation_id: string;
  source_id: string;
  title: string;
  authors: string[];
  year?: number | null;
  venue?: string | null;
  doi?: string | null;
  canonical_url: string;
  evidence_ids: string[];
}

export interface Report {
  id: string;
  task_id: string;
  title: string;
  executive_summary: string;
  findings: Record<string, any>;
  common_ground: string;
  uncertainty_and_gaps: string;
  methodology: string;
  limitations: string;
  citations: Citation[];
  status: string;
  created_at: string;
}

export interface Task {
  id: string;
  claim: string;
  status: TaskStatus;
  config: {
    max_rounds?: number;
    max_queries?: number;
    max_sources?: number;
    max_page_fetches?: number;
    allow_full_text_fetch?: boolean;
  };
  error_message?: string | null;
  created_at: string;
  updated_at: string;
  completed_at?: string | null;
  subclaims: Subclaim[];
  sources_count: number;
  evidence_count: number;
  has_report: boolean;
  sources?: Source[];
}

export const ClaimSubmissionSchema = z.object({
  claim: z
    .string()
    .min(10, "Claim must be at least 10 characters long")
    .max(1000, "Claim must not exceed 1000 characters"),
  max_rounds: z.number().min(1).max(5).default(3),
  max_queries: z.number().min(1).max(30).default(15),
  max_sources: z.number().min(5).max(100).default(40),
  allow_full_text_fetch: z.boolean().default(true),
});

export type ClaimSubmissionForm = z.infer<typeof ClaimSubmissionSchema>;
