from typing import List

from ..core.logging import get_logger
from ..db.models import Evidence, ResearchTask, Source, Subclaim
from ..providers.base import LLMProvider
from ..schemas.llm_payloads import ReportSynthesisOutput

logger = get_logger(__name__)

SYNTHESIS_SYSTEM_PROMPT = """
You are a senior academic systematic review specialist and chief scientific officer.
Synthesize the verified evidence collected from OpenAlex and Crossref into a balanced, rigorous, peer-review-grade research report.

Guidelines:
1. Executive Summary: State the current state of scholarly consensus neutrally. Highlight both empirical benefits and documented risks/counter-evidence.
2. Common Ground: Synthesize points on which disparate studies and methodologies agree.
3. Uncertainty & Evidence Gaps: Explicitly outline areas where evidence is thin, conflicting, or non-causal.
4. Methodology: Detail the systematic discovery, deduplication, and evidence extraction process.
5. Limitations: Explicitly state the boundaries of the retrieved evidence base.
6. Absolute Traceability: Do not fabricate citations or claim consensus that is not substantiated by the provided evidence items.
"""


class ReportSynthesizer:
    def __init__(self, llm: LLMProvider):
        self.llm = llm

    async def generate_report(
        self,
        task: ResearchTask,
        subclaims: List[Subclaim],
        sources: List[Source],
        evidence_items: List[Evidence],
        queries_run: List[str],
    ) -> ReportSynthesisOutput:
        # Build evidence dossiers for prompt
        source_lookup = {s.id: s for s in sources}
        subclaim_lookup = {sc.id: sc for sc in subclaims}

        evidence_summaries = []
        for i, ev in enumerate(evidence_items, 1):
            s = source_lookup.get(ev.source_id)
            sc = subclaim_lookup.get(ev.subclaim_id)
            s_title = s.title if s else "Unknown Source"
            s_year = s.year or "n.d."
            sc_text = sc.subclaim_text if sc else "General"
            is_peer = "Peer-Reviewed" if (s and s.is_peer_reviewed) else "Preprint/Report"

            evidence_summaries.append(
                f"[{i}] Subclaim: {sc_text}\n"
                f"    Relationship: {ev.relationship.upper()}\n"
                f'    Source: "{s_title}" ({s_year}, {is_peer})\n'
                f'    Passage: "{ev.passage[:250]}..."\n'
                f"    Rationale: {ev.rationale}\n"
                f"    Limitations: {ev.limitations}\n"
            )

        dossier = (
            "\n".join(evidence_summaries) if evidence_summaries else "No formal evidence extracted."
        )

        prompt = (
            f'Research Claim: "{task.claim}"\n\n'
            f"Verified Evidence Dossier ({len(evidence_items)} items across {len(sources)} unique scholarly sources):\n"
            f"{dossier}\n\n"
            f"Systematic Search Scope:\n"
            f"- Search Queries Executed: {len(queries_run)}\n"
            f"- Queries: {', '.join(queries_run[:8])}\n"
            f"- Scholarly Indices: OpenAlex, Crossref\n\n"
            f"Please generate the comprehensive research report."
        )

        return await self.llm.generate_structured(
            prompt=prompt,
            system_prompt=SYNTHESIS_SYSTEM_PROMPT,
            response_model=ReportSynthesisOutput,
        )
