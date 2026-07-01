# -*- coding: utf-8 -*-
"""Structured data models for the email-campaign-designer harness.

Pure standard-library ``dataclasses`` (no pydantic / third-party dependency) so the
package runs in fully offline / sandboxed environments. Each model corresponds to a
stage contract documented in ``skills/main.md`` and the ``skills/sub-*.md`` specs.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Dict, List, Optional


class Certainty(str, Enum):
    """Confidence grade for an assertion, following the evidence hierarchy."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    STALE = "stale"

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.value


@dataclass
class Evidence:
    """A single citable source used to justify a score or finding."""

    citation: str
    url: Optional[str] = None
    framework: Optional[str] = None
    certainty: Certainty = Certainty.MEDIUM

    def to_markdown(self) -> str:
        link = f" <{self.url}>" if self.url else ""
        tag = f" [{self.framework}]" if self.framework else ""
        cert = f" (certainty: {self.certainty})"
        return f"- {self.citation}{tag}{link}{cert}"


@dataclass
class Segment:
    """An audience segment produced by the intake / segmentation stage."""

    name: str
    description: str
    recency_days: Optional[int] = None
    frequency: Optional[int] = None
    monetary: Optional[float] = None
    rfm_label: Optional[str] = None
    size: Optional[int] = None
    personalization_tokens: List[str] = field(default_factory=list)


@dataclass
class EmailMessage:
    """A single email in the designed campaign sequence."""

    position: int
    name: str
    segment: str
    subject_line: str
    preview_text: str = ""
    body: str = ""
    cta_primary: str = ""
    cta_secondary: str = ""
    send_delay_days: int = 0
    has_unsubscribe: bool = True
    has_physical_address: bool = True
    has_consent_basis: bool = True

    @property
    def subject_length(self) -> int:
        return len(self.subject_line)

    @property
    def cta_count(self) -> int:
        return sum(1 for c in (self.cta_primary, self.cta_secondary) if c)


@dataclass
class FrameworkChoice:
    """A framework selected by ``sub-framework-selector`` with justification."""

    name: str
    role: str
    justification: str
    covers: List[str] = field(default_factory=list)


@dataclass
class DimensionScore:
    """Score for one rubric dimension with cited evidence."""

    dimension: str
    weight: float
    score: int
    rationale: str
    evidence: List[Evidence] = field(default_factory=list)
    sub_scores: Dict[str, int] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not 0 <= self.score <= 100:
            raise ValueError(
                f"dimension score out of range [0,100]: {self.dimension}={self.score}"
            )


@dataclass
class Scorecard:
    """Aggregated weighted score and letter grade."""

    dimensions: List[DimensionScore] = field(default_factory=list)
    overall: float = 0.0
    grade: str = "D"

    def by_name(self, name: str) -> Optional[DimensionScore]:
        for d in self.dimensions:
            if d.dimension == name:
                return d
        return None


@dataclass
class ComplianceFinding:
    """A single compliance issue or pass recorded by ``sub-compliance-check``."""

    rule: str
    status: str  # "pass" | "warn" | "fail"
    detail: str
    evidence: Optional[Evidence] = None
    needs_legal_review: bool = False


@dataclass
class RoadmapItem:
    """A prioritised improvement recommendation traceable to a finding."""

    title: str
    finding: str
    effort: int  # 1 (low) .. 5 (high)
    impact: int  # 1 (low) .. 5 (high)
    dimension: Optional[str] = None
    evidence: Optional[Evidence] = None

    @property
    def priority(self) -> float:
        """impact / effort ratio; higher is more attractive to do first."""
        return self.impact / max(1, self.effort)

    @property
    def quadrant(self) -> str:
        if self.impact >= 4 and self.effort <= 2:
            return "quick-win"
        if self.impact >= 4 and self.effort >= 3:
            return "major-project"
        if self.impact <= 2 and self.effort <= 2:
            return "fill-in"
        return "thankless"


@dataclass
class ChallengeResult:
    """Devil's-advocate review of the scored conclusions."""

    assumptions: List[str] = field(default_factory=list)
    disconfirming_evidence: List[Evidence] = field(default_factory=list)
    certainty_overall: Certainty = Certainty.MEDIUM
    summary: str = ""


@dataclass
class CampaignReport:
    """The final synthesised deliverable emitted by the harness."""

    executive_summary: str
    context: str
    frameworks: List[FrameworkChoice]
    segments: List[Segment]
    emails: List[EmailMessage]
    scorecard: Scorecard
    findings: List[str]
    risks: List[str]
    roadmap: List[RoadmapItem]
    compliance: List[ComplianceFinding]
    challenge: ChallengeResult
    limitations: List[str]
    sources: List[Evidence]
    degraded: bool = False
    gates_passed: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CampaignBrief:
    """Intake bundle collected by ``sub-intake``."""

    objective: str
    campaign_type: str  # welcome | re-engagement | cold-outreach | promotional | newsletter | transactional
    audience_description: str
    segments: List[Segment] = field(default_factory=list)
    emails: List[EmailMessage] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    goals: List[str] = field(default_factory=list)
    jurisdiction: str = "US"  # US | EU | UK | CA | mixed
    consent_basis: Optional[str] = None
    sender_domain: Optional[str] = None
    offline: bool = False
    notes: str = ""
    clarifying_questions: List[str] = field(default_factory=list)

    def is_complete(self) -> bool:
        """A brief is runnable once objective, type and audience are present."""
        return bool(self.objective and self.campaign_type and self.audience_description)
