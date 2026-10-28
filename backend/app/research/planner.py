from typing import List

from ..core.logging import get_logger
from ..providers.base import LLMProvider
from ..schemas.llm_payloads import CounterEvidenceGapOutput, SubclaimPlanningOutput

logger = get_logger(__name__)

PLANNER_SYSTEM_PROMPT = """
You are an expert scholarly research planner.
Your role is to decompose research claims into specific, empirical, testable subclaims, and generate effective academic search queries suitable for scientific databases like OpenAlex and Crossref.

Requirements:
1. Decompose the claim into 2 to 4 distinct testable facets (e.g. primary effect, quality/safety implications, long-term costs, human factors).
2. For each subclaim, formulate 2 to 3 targeted academic search queries using standard scholarly keywords.
3. Be neutral, objective, and empirical. Do not assume the claim is true.
"""

COUNTER_QUERY_SYSTEM_PROMPT = """
You are an expert scholarly adversarial researcher seeking balance and counter-evidence.
Analyze the current research findings, identify evidence gaps or publication bias, and formulate queries specifically designed to surface contradictory evidence, negative results, refutations, or boundary conditions.
"""


class ResearchPlanner:
    def __init__(self, llm: LLMProvider):
        self.llm = llm

    async def decompose_claim(self, claim: str) -> SubclaimPlanningOutput:
        prompt = (
            f'Research Claim to Investigate:\n"{claim}"\n\n'
            f"Please decompose this claim into testable empirical subclaims and provide targeted scholarly search queries."
        )
        return await self.llm.generate_structured(
            prompt=prompt,
            system_prompt=PLANNER_SYSTEM_PROMPT,
            response_model=SubclaimPlanningOutput,
        )

    async def identify_gaps_and_counter_queries(
        self,
        claim: str,
        subclaims: List[str],
        found_evidence_summaries: List[str],
    ) -> CounterEvidenceGapOutput:
        evidence_text = (
            "\n".join(f"- {s}" for s in found_evidence_summaries)
            if found_evidence_summaries
            else "No decisive contradictory evidence gathered yet."
        )
        subclaims_text = "\n".join(f"- {sc}" for sc in subclaims)

        prompt = (
            f'Original Claim: "{claim}"\n\n'
            f"Subclaims:\n{subclaims_text}\n\n"
            f"Current Evidence Gathered So Far:\n{evidence_text}\n\n"
            f"Analyze the gaps in this evidence base. Specifically formulate targeted counter-evidence queries "
            f"aimed at finding negative results, defects, overheads, developer frustration, or studies refuting the claim."
        )
        return await self.llm.generate_structured(
            prompt=prompt,
            system_prompt=COUNTER_QUERY_SYSTEM_PROMPT,
            response_model=CounterEvidenceGapOutput,
        )
