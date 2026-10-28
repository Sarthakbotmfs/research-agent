from typing import List

from ..core.logging import get_logger
from ..providers.base import LLMProvider
from ..schemas.enums import EvidenceRelationshipEnum
from ..schemas.llm_payloads import EvidenceClassificationItem, EvidenceClassificationOutput

logger = get_logger(__name__)

CLASSIFIER_SYSTEM_PROMPT = """
You are a rigorous academic evidence classifier specializing in research synthesis.
Evaluate the provided scholarly source text against a specific subclaim.

Your task:
1. Determine the empirical relationship:
   - "supports": Source findings directly substantiate the subclaim with empirical data.
   - "contradicts": Source findings directly refute, disprove, or conflict with the subclaim.
   - "mixed": Source shows conflicting results, strong tradeoffs, or conditional benefits/drawbacks.
   - "context": Source provides background theory or methodology without directly testing the subclaim.
   - "insufficient": Source mentions the topic but lacks empirical data, or sample size is inadequate.

2. Extract an EXACT, VERBATIM excerpt from the source text that substantiates your verdict. Do not invent words.
3. Formulate a concise rationale detailing the methodology, effect size, or study design.
4. Note key limitations (sample size, threats to validity, correlational vs causal).
5. Assign an objective confidence score from 0.0 to 1.0.
"""


class EvidenceClassifier:
    def __init__(self, llm: LLMProvider):
        self.llm = llm

    async def classify_evidence(
        self,
        subclaim_id: str,
        subclaim_text: str,
        source_title: str,
        source_text: str,
        is_peer_reviewed: bool,
    ) -> List[EvidenceClassificationItem]:
        # Limit source text length sent to LLM to prevent token blowup
        truncated_text = source_text[:4000]

        prompt = (
            f"Subclaim ID: {subclaim_id}\n"
            f'Subclaim Text: "{subclaim_text}"\n\n'
            f"Source Title: {source_title}\n"
            f"Peer-Reviewed: {is_peer_reviewed}\n\n"
            f'Source Text:\n"""{truncated_text}"""\n\n'
            f"Classify how this source text relates to the subclaim. Quote an exact passage from the source text."
        )

        try:
            result = await self.llm.generate_structured(
                prompt=prompt,
                system_prompt=CLASSIFIER_SYSTEM_PROMPT,
                response_model=EvidenceClassificationOutput,
            )
            # Ensure items have valid subclaim_id
            for item in result.evaluations:
                item.subclaim_id = subclaim_id
                # If exact passage is empty, use first 250 characters of source text
                if not item.exact_passage or len(item.exact_passage.strip()) < 10:
                    item.exact_passage = truncated_text[:300].strip()
            return result.evaluations
        except Exception as e:
            logger.warning(f"Error classifying evidence for subclaim {subclaim_id}: {e}")
            # Return a defensive fallback classification
            return [
                EvidenceClassificationItem(
                    subclaim_id=subclaim_id,
                    relationship=EvidenceRelationshipEnum.INSUFFICIENT,
                    exact_passage=truncated_text[:250].strip() or "Abstract unavailable",
                    rationale=f"Automated classification encountered processing issue: {e}",
                    limitations="Source text could not be reliably classified by model.",
                    confidence_score=0.2,
                )
            ]
