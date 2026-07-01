# -*- coding: utf-8 -*-
"""``sub-intake`` - Intake & Context Gathering.

Collects and validates the structured brief needed to run the analysis and emits
targeted clarifying questions when key facts are missing. Pure deterministic logic
so it can run fully offline; the harness may later enrich the brief with WebSearch
results before continuing.
"""
from __future__ import annotations

from typing import List, Optional

from .schemas import CampaignBrief, Segment


REQUIRED_FIELDS = ("objective", "campaign_type", "audience_description")

CAMPAIGN_TYPES = {
    "welcome",
    "re-engagement",
    "cold-outreach",
    "promotional",
    "newsletter",
    "transactional",
}

JURISDICTIONS = {"US", "EU", "UK", "CA", "mixed"}


class Intake:
    """Normalises a raw request into a validated ``CampaignBrief``."""

    def collect(self, raw: dict) -> CampaignBrief:
        """Build a ``CampaignBrief`` from a loose dict, applying sensible defaults."""
        brief = CampaignBrief(
            objective=str(raw.get("objective", "")).strip(),
            campaign_type=str(raw.get("campaign_type", "")).strip().lower(),
            audience_description=str(raw.get("audience_description", "")).strip(),
            constraints=[str(c).strip() for c in raw.get("constraints", []) if str(c).strip()],
            goals=[str(g).strip() for g in raw.get("goals", []) if str(g).strip()],
            jurisdiction=str(raw.get("jurisdiction", "US")).strip().upper(),
            consent_basis=raw.get("consent_basis"),
            sender_domain=raw.get("sender_domain"),
            offline=bool(raw.get("offline", False)),
            notes=str(raw.get("notes", "")).strip(),
        )
        for seg in raw.get("segments", []) or []:
            brief.segments.append(self._segment(seg))
        return brief

    @staticmethod
    def _segment(seg: dict) -> Segment:
        return Segment(
            name=str(seg.get("name", "")).strip(),
            description=str(seg.get("description", "")).strip(),
            recency_days=seg.get("recency_days"),
            frequency=seg.get("frequency"),
            monetary=seg.get("monetary"),
            rfm_label=seg.get("rfm_label"),
            size=seg.get("size"),
            personalization_tokens=[
                str(t).strip() for t in seg.get("personalization_tokens", []) if str(t).strip()
            ],
        )

    def clarify(self, brief: CampaignBrief) -> List[str]:
        """Return targeted clarifying questions for any missing key fact."""
        questions: List[str] = []
        if not brief.objective:
            questions.append("What is the primary objective of this campaign (e.g. activate, retain, convert)?")
        if not brief.campaign_type:
            questions.append("Which campaign type: welcome, re-engagement, cold-outreach, promotional, newsletter or transactional?")
        elif brief.campaign_type not in CAMPAIGN_TYPES:
            questions.append(
                f"Unknown campaign type '{brief.campaign_type}'. Use one of: {', '.join(sorted(CAMPAIGN_TYPES))}."
            )
        if not brief.audience_description:
            questions.append("Describe the target audience (size, source, behaviour) so segmentation can be grounded.")
        if not brief.segments:
            questions.append("Are pre-defined segments available, or should RFM/behavioural segments be derived?")
        if brief.jurisdiction not in JURISDICTIONS:
            questions.append(f"Unknown jurisdiction '{brief.jurisdiction}'. Use one of: {', '.join(sorted(JURISDICTIONS))}.")
        if brief.jurisdiction in {"EU", "UK", "mixed"} and not brief.consent_basis:
            questions.append("For EU/UK traffic, state the GDPR consent/lawful-basis (opt-in, legitimate interest, contract).")
        if not brief.sender_domain and brief.campaign_type == "cold-outreach":
            questions.append("Provide the sending domain so SPF/DKIM/DMARC posture can be assessed.")
        if not brief.goals:
            questions.append("State at least one measurable goal (e.g. target open rate, CTR, conversions).")
        return questions

    def is_runnable(self, brief: CampaignBrief) -> bool:
        return brief.is_complete() and not self.clarify(brief)

    def ensure_runnable(self, brief: CampaignBrief) -> CampaignBrief:
        """Attach clarifying questions to the brief; leaves the harness to re-ask."""
        brief.clarifying_questions = self.clarify(brief)
        return brief
