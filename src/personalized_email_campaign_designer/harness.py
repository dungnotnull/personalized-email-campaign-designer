# -*- coding: utf-8 -*-
"""Harness - end-to-end orchestrator (mirrors ``skills/main.md``).

Stages: intake -> framework selection -> research (degraded fallback) -> scoring
-> challenge -> compliance gate -> roadmap -> synthesise -> quality gates.

The harness is deterministic and offline-safe. If ``brief.offline`` is True (or no
live research tool is supplied) it degrades to the local SECOND-KNOWLEDGE-BRAIN and
marks the report accordingly.
"""
from __future__ import annotations

import os
from typing import Callable, List, Optional

from .compliance_check import ComplianceChecker
from .framework_selector import FrameworkSelector
from .improvement_roadmap import ImprovementRoadmap
from .intake import Intake
from .knowledge_brain import KnowledgeBrain
from .scoring_engine import ScoringEngine
from .synthesizer import Synthesizer
from .challenge import Challenger
from .schemas import (
    CampaignBrief,
    CampaignReport,
    Certainty,
    ChallengeResult,
    Evidence,
    Scorecard,
    Segment,
    EmailMessage,
)


# A live-research hook (optional). Signature: query -> list[Evidence].
ResearchFn = Callable[[str], List[Evidence]]


class Harness:
    def __init__(
        self,
        brain_path: Optional[str] = None,
        research_fn: Optional[ResearchFn] = None,
    ):
        self.intake = Intake()
        self.selector = FrameworkSelector()
        self.scorer = ScoringEngine()
        self.challenger = Challenger()
        self.compliance = ComplianceChecker()
        self.roadmap = ImprovementRoadmap()
        self.synthesizer = Synthesizer()
        self.brain = KnowledgeBrain(brain_path)
        self.research_fn = research_fn

    # ---- public API -------------------------------------------------------

    def run(self, raw_brief: dict) -> CampaignReport:
        """Run the full harness over a raw brief dict and return the report."""
        brief = self.intake.collect(raw_brief)
        brief = self.intake.ensure_runnable(brief)
        if not self.intake.is_runnable(brief):
            return self._clarification_report(brief)
        return self._execute(brief, brief.segments, brief.emails)

    def run_with_design(self, brief: CampaignBrief, segments: List[Segment], emails: List[EmailMessage]) -> CampaignReport:
        """Run the harness over an already-designed campaign (brief + emails)."""
        return self._execute(brief, segments, emails)

    # ---- internal ---------------------------------------------------------

    def _execute(self, brief: CampaignBrief, segments: List[Segment], emails: List[EmailMessage]) -> CampaignReport:
        degraded = brief.offline or self.research_fn is None
        # Stage 2: framework selection.
        frameworks = self.selector.select(brief.campaign_type, brief.jurisdiction)
        # Stage 3: research (degrade gracefully).
        evidence_pool = self._research(brief, frameworks, degraded)
        # Stage 4: scoring.
        scorecard = self.scorer.score(brief, segments, emails, degraded=degraded)
        # Stage 5: challenge.
        challenge = self.challenger.review(brief, scorecard, emails)
        # Stage 6: compliance gate.
        compliance = self.compliance.check(brief, emails)
        # Stage 7: roadmap.
        roadmap = self.roadmap.build(brief, scorecard, compliance, segments, emails)
        # Synthesise + gates.
        gates_passed = self._quality_gates(scorecard, compliance, roadmap, challenge)
        findings, risks = self._findings(scorecard, compliance)
        sources = self._collect_sources(scorecard, compliance, frameworks)
        report = CampaignReport(
            executive_summary=self._exec_summary(brief, scorecard, compliance, degraded),
            context=self._context(brief, segments, emails),
            frameworks=frameworks,
            segments=segments,
            emails=emails,
            scorecard=scorecard,
            findings=findings,
            risks=risks,
            roadmap=roadmap,
            compliance=compliance,
            challenge=challenge,
            limitations=self._limitations(brief, degraded, challenge),
            sources=sources,
            degraded=degraded,
            gates_passed=gates_passed,
        )
        return report

    def _research(self, brief, frameworks, degraded) -> List[Evidence]:
        if self.research_fn is not None:
            try:
                return self.research_fn(brief.objective)
            except Exception:
                degraded = True
        # degraded: pull benchmark lines from the brain.
        if not self.brain.exists():
            return []
        hits = self.brain.search(brief.objective + " email " + brief.campaign_type, limit=10)
        return [Evidence(line.strip("- "), certainty=Certainty.STALE) for line in hits if line.strip()]

    # ---- gates ------------------------------------------------------------

    def _quality_gates(self, scorecard, compliance, roadmap, challenge) -> bool:
        # 1. every score cites a source/framework
        for d in scorecard.dimensions:
            if not d.evidence:
                return False
        # 2. challenge completed
        if not challenge.summary:
            return False
        # 3. roadmap traceable
        if not roadmap:
            return False
        # 4. compliance: passes block release (failures may still ship if flagged)
        if self.compliance.blocks_release(compliance):
            return False
        return True

    # ---- report helpers ----------------------------------------------------

    def _exec_summary(self, brief, scorecard, compliance, degraded):
        verdict = self.compliance.summary(compliance)
        mode = "degraded (offline) mode" if degraded else "live-research mode"
        return (
            f"{brief.objective} - Overall grade **{scorecard.grade} ({scorecard.overall}/100)** "
            f"in {mode}. {verdict} Strongest dimension: "
            f"{max(scorecard.dimensions, key=lambda d: d.score).dimension}; "
            f"weakest: {min(scorecard.dimensions, key=lambda d: d.score).dimension}."
        )

    @staticmethod
    def _context(brief, segments, emails):
        return (
            f"Objective: {brief.objective}. Campaign type: {brief.campaign_type}. "
            f"Jurisdiction: {brief.jurisdiction}. Audience: {brief.audience_description}. "
            f"{len(segments)} segment(s), {len(emails)} email(s) designed."
        )

    def _findings(self, scorecard, compliance):
        findings, risks = [], []
        for d in scorecard.dimensions:
            if d.score >= 85:
                findings.append(f"{d.dimension}: strong ({d.score}/100) - {d.rationale}")
            elif d.score < 60:
                risks.append(f"{d.dimension}: weak ({d.score}/100) - {d.rationale}")
            else:
                findings.append(f"{d.dimension}: adequate ({d.score}/100) - {d.rationale}")
        for c in compliance:
            if c.status == "fail":
                risks.append(f"Compliance fail [{c.rule}]: {c.detail}")
            elif c.status == "warn":
                findings.append(f"Compliance warning [{c.rule}]: {c.detail}")
        return findings, risks

    @staticmethod
    def _limitations(brief, degraded, challenge):
        lim = []
        if degraded:
            lim.append("Live research unavailable; scores use local SECOND-KNOWLEDGE-BRAIN benchmarks (may be stale).")
        if not brief.sender_domain:
            lim.append("Sender authentication not verified; deliverability score assumes compliant SPF/DKIM/DMARC.")
        if not brief.goals:
            lim.append("No measurable goals supplied; conversion impact is qualitative.")
        lim.append(f"Overall certainty: {challenge.certainty_overall}.")
        return lim

    @staticmethod
    def _collect_sources(scorecard, compliance, frameworks):
        sources = []
        for d in scorecard.dimensions:
            sources.extend(d.evidence)
        for c in compliance:
            if c.evidence:
                sources.append(c.evidence)
        seen = set()
        unique = []
        for s in sources:
            key = s.citation
            if key in seen:
                continue
            seen.add(key)
            unique.append(s)
        return unique

    def _clarification_report(self, brief: CampaignBrief) -> CampaignReport:
        summary = "Intake incomplete. Please answer the clarifying questions before running the full analysis."
        return CampaignReport(
            executive_summary=summary,
            context=brief.objective or "(no objective supplied)",
            frameworks=[],
            segments=brief.segments,
            emails=brief.emails,
            scorecard=Scorecard(),
            findings=[f"Clarifying question: {q}" for q in brief.clarifying_questions],
            risks=["Cannot score until intake is complete."],
            roadmap=[],
            compliance=[],
            challenge=ChallengeResult(summary="Intake incomplete.", certainty_overall=Certainty.LOW),
            limitations=["Harness blocked at intake; no scoring performed."],
            sources=[],
            degraded=True,
            gates_passed=False,
        )
