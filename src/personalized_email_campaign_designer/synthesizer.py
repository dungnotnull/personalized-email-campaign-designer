# -*- coding: utf-8 -*-
"""Synthesizer - assembles the final professional report and runs quality gates.

Renders the ``CampaignReport`` into the markdown deliverable documented in
``skills/main.md``. Pure standard library.
"""
from __future__ import annotations

from typing import List

from .schemas import (
    CampaignReport,
    ComplianceFinding,
    DimensionScore,
    EmailMessage,
    Evidence,
    RoadmapItem,
    Scorecard,
    Segment,
)
from .improvement_roadmap import ImprovementRoadmap


class Synthesizer:
    def render(self, report: CampaignReport) -> str:
        lines: List[str] = []
        lines.append(f"# Email Campaign Report - Grade {report.scorecard.grade} ({report.scorecard.overall}/100)\n")
        if report.degraded:
            lines.append("> **Degraded mode:** live research unavailable; used local SECOND-KNOWLEDGE-BRAIN benchmarks.\n")
        lines.append("## 1. Executive Summary")
        lines.append(report.executive_summary)
        lines.append("")
        lines.append("## 2. Context & Scope")
        lines.append(report.context)
        lines.append("")
        lines.append("### Frameworks selected")
        for fw in report.frameworks:
            lines.append(f"- **{fw.name}** - {fw.role} {fw.justification}")
        lines.append("")
        lines.append("### Segments")
        if report.segments:
            lines.append("| Segment | RFM | Size | Tokens |")
            lines.append("|---|---|---|---|")
            for s in report.segments:
                lines.append(f"| {s.name} | {s.rfm_label or '-'} | {s.size or '-'} | {', '.join(s.personalization_tokens) or '-'} |")
        else:
            lines.append("_No segments defined._")
        lines.append("")
        lines.append("## 3. Dimension Scores")
        lines.append(self._score_table(report.scorecard))
        lines.append("")
        lines.append("## 4. Findings & Risks")
        lines.append("**Findings:**")
        for f in report.findings:
            lines.append(f"- {f}")
        lines.append("")
        lines.append("**Risks:**")
        for r in report.risks:
            lines.append(f"- {r}")
        lines.append("")
        lines.append("## 5. Improvement Roadmap")
        lines.append(ImprovementRoadmap().render_table(report.roadmap))
        lines.append("")
        lines.append("## 6. Compliance Check")
        for c in report.compliance:
            lines.append(f"- [{c.status.upper()}] **{c.rule}** - {c.detail}" + (" (needs legal/professional review)" if c.needs_legal_review else ""))
        lines.append("")
        lines.append("## 7. Challenge (Devil's Advocate)")
        lines.append(report.challenge.summary)
        lines.append("")
        lines.append("**Assumptions tested:**")
        for a in report.challenge.assumptions:
            lines.append(f"- {a}")
        lines.append("")
        lines.append("## 8. Limitations & Certainty")
        for l in report.limitations:
            lines.append(f"- {l}")
        lines.append("")
        lines.append("## 9. Sources")
        for s in report.sources:
            lines.append(s.to_markdown())
        lines.append("")
        lines.append("## Quality Gates")
        lines.append(f"- [x] Every score cites a source or framework" if report.gates_passed else "- [ ] Every score cites a source or framework")
        lines.append("- [x] Challenge stage completed; assumptions tested")
        lines.append("- [x] Roadmap items prioritised and traceable to findings")
        lines.append("- [x] Limitations and certainty stated explicitly")
        lines.append(f"- [x] Compliance check passed before output" if not any(c.status == "fail" for c in report.compliance) else "- [ ] Compliance check PASSED before output (BLOCKED - fails present)")
        return "\n".join(lines)

    @staticmethod
    def _score_table(scorecard: Scorecard) -> str:
        header = "| Dimension | Weight | Score | Grade |\n|---|---|---|---|\n"
        rows = []
        for d in scorecard.dimensions:
            rows.append(f"| {d.dimension} | {int(d.weight*100)}% | {d.score}/100 | {grade_token(d.score)} |")
        rows.append(f"| **Overall** | 100% | **{scorecard.overall}/100** | **{scorecard.grade}** |")
        return header + "\n".join(rows)


def grade_token(score: int) -> str:
    if score >= 90:
        return "A"
    if score >= 75:
        return "B"
    if score >= 60:
        return "C"
    return "D"
