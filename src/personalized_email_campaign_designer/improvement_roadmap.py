# -*- coding: utf-8 -*-
"""``sub-improvement-roadmap`` - Improvement Roadmap.

Translates scored findings and compliance issues into a prioritised, effort x
impact ranked set of recommendations traceable to the rubric. Items are sorted by
impact/effort ratio and bucketed into quadrants (quick-win, major-project, fill-in,
thankless) for clear execution guidance.
"""
from __future__ import annotations

from typing import List

from .schemas import (
    CampaignBrief,
    ComplianceFinding,
    DimensionScore,
    EmailMessage,
    Evidence,
    RoadmapItem,
    Scorecard,
    Segment,
    Certainty,
)


class ImprovementRoadmap:
    """Build a prioritised roadmap from a scorecard + compliance audit."""

    def build(
        self,
        brief: CampaignBrief,
        scorecard: Scorecard,
        compliance: List[ComplianceFinding],
        segments: List[Segment],
        emails: List[EmailMessage],
    ) -> List[RoadmapItem]:
        items: List[RoadmapItem] = []
        items.extend(self._from_scores(scorecard))
        items.extend(self._from_compliance(compliance))
        items.extend(self._from_segments(segments))
        items.extend(self._from_emails(emails))
        # de-duplicate by title while keeping the highest-priority instance
        seen = {}
        for it in items:
            key = it.title.lower()
            if key not in seen or it.priority > seen[key].priority:
                seen[key] = it
        ranked = sorted(seen.values(), key=lambda i: (i.priority, i.impact), reverse=True)
        return ranked

    def render_table(self, items: List[RoadmapItem]) -> str:
        header = "| # | Title | Dimension | Effort | Impact | Quadrant | Finding |\n|---|---|---|---|---|---|---|\n"
        rows = []
        for i, it in enumerate(items, 1):
            rows.append(f"| {i} | {it.title} | {it.dimension or '-'} | {it.effort} | {it.impact} | {it.quadrant} | {it.finding} |")
        return header + "\n".join(rows)

    # ---- generators -------------------------------------------------------

    def _from_scores(self, scorecard: Scorecard) -> List[RoadmapItem]:
        out: List[RoadmapItem] = []
        for d in scorecard.dimensions:
            if d.score >= 85:
                continue
            effort, impact = self._effort_impact(d)
            title = self._title_for(d)
            out.append(RoadmapItem(
                title=title, finding=f"{d.dimension} scored {d.score}/100.",
                effort=effort, impact=impact, dimension=d.dimension,
                evidence=d.evidence[0] if d.evidence else None,
            ))
        return out

    def _from_compliance(self, compliance: List[ComplianceFinding]) -> List[RoadmapItem]:
        out: List[RoadmapItem] = []
        for f in compliance:
            if f.status == "pass":
                continue
            impact = 5 if f.status == "fail" else 3
            effort = 2 if "unsubscribe" in f.detail.lower() or "physical" in f.detail.lower() else 3
            out.append(RoadmapItem(
                title=f"Resolve compliance issue: {f.rule}",
                finding=f.detail, effort=effort, impact=impact,
                dimension="Deliverability & compliance", evidence=f.evidence,
            ))
        return out

    def _from_segments(self, segments: List[Segment]) -> List[RoadmapItem]:
        out: List[RoadmapItem] = []
        if not segments:
            out.append(RoadmapItem(title="Define at least 2 RFM segments",
                finding="No segments provided; personalization is generic.",
                effort=2, impact=4, dimension="Segmentation & personalization",
                evidence=Evidence("RFM segmentation improves targeting precision.", framework="RFM", certainty=Certainty.MEDIUM)))
        else:
            missing_rfm = [s.name for s in segments if not s.rfm_label]
            if missing_rfm:
                out.append(RoadmapItem(title="Attach RFM labels to segments",
                    finding=f"Segments without RFM labels: {', '.join(missing_rfm)}.",
                    effort=1, impact=3, dimension="Segmentation & personalization",
                    evidence=Evidence("RFM labels drive recency/monetary targeting.", framework="RFM", certainty=Certainty.MEDIUM)))
            low_tokens = [s.name for s in segments if len(s.personalization_tokens) < 2]
            if low_tokens:
                out.append(RoadmapItem(title="Add >=2 personalization tokens per segment",
                    finding=f"Thin personalization in: {', '.join(low_tokens)}.",
                    effort=1, impact=3, dimension="Segmentation & personalization"))
        return out

    def _from_emails(self, emails: List[EmailMessage]) -> List[RoadmapItem]:
        out: List[RoadmapItem] = []
        for e in emails:
            if not (28 <= e.subject_length <= 50):
                out.append(RoadmapItem(
                    title=f"Shorten/lengthen subject line for '{e.name}'",
                    finding=f"Subject length {e.subject_length} outside 28-50 char ideal band.",
                    effort=1, impact=3, dimension="Subject & preview (open rate)"))
            if not e.preview_text:
                out.append(RoadmapItem(
                    title=f"Add preview text to '{e.name}'",
                    finding="Empty preview text wastes the inbox preview pane.",
                    effort=1, impact=3, dimension="Subject & preview (open rate)"))
            if e.cta_count != 1:
                out.append(RoadmapItem(
                    title=f"Use a single primary CTA in '{e.name}'",
                    finding=f"{e.cta_count} CTAs detected; competing CTAs reduce clicks.",
                    effort=1, impact=4, dimension="Persuasion & copy quality"))
        return out

    # ---- helpers ----------------------------------------------------------

    @staticmethod
    def _effort_impact(d: DimensionScore):
        # lower-scoring dimensions get higher impact; copy fixes are cheap.
        gap = 100 - d.score
        impact = 5 if gap > 30 else (4 if gap > 15 else 3)
        if "Subject" in d.dimension or "Persuasion" in d.dimension or "Conversion" in d.dimension:
            effort = 2
        elif "Deliverability" in d.dimension:
            effort = 3
        else:
            effort = 2
        return effort, impact

    @staticmethod
    def _title_for(d: DimensionScore) -> str:
        weak = sorted(d.sub_scores.items(), key=lambda kv: kv[1])
        if weak:
            return f"Improve {d.dimension.lower()}: focus on '{weak[0][0]}'"
        return f"Improve {d.dimension.lower()}"
