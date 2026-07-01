# -*- coding: utf-8 -*-
"""``sub-framework-selector`` - Evaluation Framework Selector.

Selects the smallest set of named, world-renowned frameworks that fully cover the
case and justifies each inclusion/exclusion. Selection is rule-driven and
deterministic so it is reproducible offline; the harness may refine choices with
live research before scoring.
"""
from __future__ import annotations

from typing import Dict, List

from .schemas import FrameworkChoice

# The canonical framework catalog for Skill #151 (citable, world-renowned).
FRAMEWORKS: Dict[str, Dict[str, str]] = {
    "AIDA": {
        "role": "Structure subject, body and CTA persuasion (Attention, Interest, Desire, Action).",
        "covers": ["copy_structure", "cta"],
    },
    "PAS": {
        "role": "Problem-Agitate-Solve copy structure for pain-driven offers.",
        "covers": ["copy_structure", "cta", "pain"],
    },
    "Cialdini": {
        "role": "Cialdini's six principles of influence: reciprocity, commitment, social proof, authority, liking, scarcity.",
        "covers": ["persuasion", "social_proof", "scarcity"],
    },
    "RFM": {
        "role": "Recency-Frequency-Monetary audience segmentation and targeting.",
        "covers": ["segmentation", "personalization"],
    },
    "SPF-DKIM-DMARC": {
        "role": "Email authentication standards for inbox placement and sender reputation.",
        "covers": ["deliverability", "authentication"],
    },
    "CAN-SPAM": {
        "role": "US CAN-SPAM Act rules: unsubscribe, physical address, no deceptive headers.",
        "covers": ["compliance", "unsubscribe", "consent_us"],
    },
    "GDPR": {
        "role": "EU/UK GDPR + ePrivacy consent, lawful basis, data-subject rights, opt-out.",
        "covers": ["compliance", "consent_eu", "unsubscribe"],
    },
    "Conversion-Design": {
        "role": "CTA placement, landing-page alignment, mobile rendering for conversion flow.",
        "covers": ["conversion", "mobile"],
    },
}


# Which coverage buckets each campaign type requires.
TYPE_COVERAGE: Dict[str, List[str]] = {
    "welcome": ["copy_structure", "cta", "persuasion", "segmentation", "deliverability", "compliance", "consent_eu", "conversion"],
    "re-engagement": ["copy_structure", "cta", "persuasion", "segmentation", "social_proof", "deliverability", "compliance", "unsubscribe"],
    "cold-outreach": ["copy_structure", "cta", "persuasion", "segmentation", "authentication", "deliverability", "compliance", "consent_us"],
    "promotional": ["copy_structure", "cta", "persuasion", "scarcity", "social_proof", "segmentation", "deliverability", "compliance"],
    "newsletter": ["copy_structure", "persuasion", "segmentation", "deliverability", "compliance", "unsubscribe"],
    "transactional": ["cta", "deliverability", "compliance", "consent_us"],
}


class FrameworkSelector:
    """Pick the smallest covering framework set and justify it."""

    def select(self, campaign_type: str, jurisdiction: str = "US") -> List[FrameworkChoice]:
        needed = set(TYPE_COVERAGE.get(campaign_type, ["copy_structure", "cta", "persuasion", "segmentation", "deliverability", "compliance"]))
        # GDPR covers EU consent; switch in GDPR for EU/UK/mixed.
        if jurisdiction in {"EU", "UK", "mixed"}:
            needed.add("consent_eu")
            needed.discard("consent_us")
        else:
            needed.add("consent_us")
            needed.discard("consent_eu")

        chosen: List[FrameworkChoice] = []
        covered: set = set()
        # Order chosen so the most load-bearing copy/segmentation frameworks come first.
        priority = ["AIDA", "PAS", "Cialdini", "RFM", "CAN-SPAM", "GDPR", "SPF-DKIM-DMARC", "Conversion-Design"]
        # CAN-SPAM is US-only; for pure EU/UK traffic GDPR + ePrivacy govern compliance.
        if jurisdiction in {"EU", "UK"}:
            priority = [n for n in priority if n != "CAN-SPAM"]
        for name in priority:
            meta = FRAMEWORKS[name]
            contributes = set(meta["covers"]) & needed - covered
            if not contributes:
                continue
            chosen.append(
                FrameworkChoice(
                    name=name,
                    role=meta["role"],
                    justification=self._justify(name, contributes, campaign_type, jurisdiction),
                    covers=sorted(contributes),
                )
            )
            covered |= contributes
        # If anything remains uncovered, force-include Conversion-Design as the catch-all.
        remaining = needed - covered
        if remaining and "Conversion-Design" not in [c.name for c in chosen]:
            chosen.append(
                FrameworkChoice(
                    name="Conversion-Design",
                    role=FRAMEWORKS["Conversion-Design"]["role"],
                    justification=f"Catch-all for uncovered coverage: {', '.join(sorted(remaining))}.",
                    covers=sorted(remaining),
                )
            )
        return chosen

    @staticmethod
    def _justify(name: str, contributes: set, campaign_type: str, jurisdiction: str) -> str:
        base = {
            "AIDA": "provides the canonical Attention-Interest-Desire-Action flow for the email body and CTA.",
            "PAS": "complements AIDA when the offer solves a concrete pain (Problem-Agitate-Solve).",
            "Cialdini": "supplies the persuasive levers (reciprocity, social proof, scarcity) that raise conversion.",
            "RFM": "grounds segmentation and personalization in Recency-Frequency-Monetary behaviour.",
            "CAN-SPAM": "is the mandatory US legal baseline (unsubscribe, physical address, non-deceptive headers).",
            "GDPR": "is the mandatory EU/UK lawful-basis and consent standard for recipients in those jurisdictions.",
            "SPF-DKIM-DMARC": "is the deliverability baseline for inbox placement and sender reputation.",
            "Conversion-Design": "aligns CTA placement, landing page and mobile rendering with the conversion flow.",
        }[name]
        return f"{name} {base} Covers: {', '.join(sorted(contributes))}."

    def exclusion_rationale(self, campaign_type: str, chosen: List[FrameworkChoice]) -> List[str]:
        chosen_names = {c.name for c in chosen}
        excluded = [n for n in FRAMEWORKS if n not in chosen_names]
        return [f"{n} excluded: its coverage ({', '.join(FRAMEWORKS[n]['covers'])}) is already met by the selected set for a {campaign_type} campaign." for n in excluded]
