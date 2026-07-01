# -*- coding: utf-8 -*-
"""Challenge stage - devil's-advocate assumption review.

Stress-tests the scored conclusions by surfacing the assumptions they rest on and
the disconfirming evidence that could change them, then assigns an overall
certainty grade. Deterministic and offline-safe.
"""
from __future__ import annotations

from typing import List

from .schemas import (
    CampaignBrief,
    Certainty,
    ChallengeResult,
    EmailMessage,
    Evidence,
    Scorecard,
)


class Challenger:
    def review(self, brief: CampaignBrief, scorecard: Scorecard, emails: List[EmailMessage]) -> ChallengeResult:
        assumptions: List[str] = []
        disconfirming: List[Evidence] = []

        if brief.offline:
            assumptions.append("Scoring used local SECOND-KNOWLEDGE-BRAIN benchmarks; live benchmarks may differ.")
            disconfirming.append(Evidence("Live open-rate benchmarks shift seasonally; stale data overstates confidence.",
                                            certainty=Certainty.STALE))
        if not brief.sender_domain:
            assumptions.append("Sender authentication assumed compliant; not actually verified in DNS.")
            disconfirming.append(Evidence("Without SPF/DKIM/DMARC checks, deliverability score is optimistic.",
                                            framework="SPF-DKIM-DMARC", certainty=Certainty.MEDIUM))
        if not brief.goals:
            assumptions.append("No measurable goal supplied; conversion success is judged qualitatively.")
        weak = [d for d in scorecard.dimensions if d.score < 60]
        if weak:
            assumptions.append(f"Weak dimensions ({', '.join(d.dimension for d in weak)}) dominate the overall grade.")

        certainty = Certainty.HIGH
        if brief.offline:
            certainty = Certainty.STALE
        elif weak or not brief.sender_domain:
            certainty = Certainty.MEDIUM

        summary = (
            f"Reviewed {len(assumptions)} assumption(s). Overall certainty: {certainty}. "
            f"Confirm the sender-domain posture and re-run with live benchmarks before high-stakes send."
        )
        return ChallengeResult(
            assumptions=assumptions,
            disconfirming_evidence=disconfirming,
            certainty_overall=certainty,
            summary=summary,
        )
