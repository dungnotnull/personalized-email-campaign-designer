# -*- coding: utf-8 -*-
"""Personalized Email Marketing Campaign Designer (Skill #151).

A research-first, framework-grounded harness that designs segmented, persuasive,
deliverable and legally compliant email campaigns, scores them on a
multi-dimensional rubric, and returns a prioritized improvement roadmap.

The package is intentionally dependency-light (Python 3.9+ standard library only)
so it can run in sandboxed / offline ("degraded") environments and fall back to the
local SECOND-KNOWLEDGE-BRAIN.md when live research tools are unavailable.

Public surface:
    - ``Harness``            end-to-end orchestrator (mirrors ``skills/main.md``).
    - ``CampaignBrief`` ...  structured data models (see ``schemas``).
    - ``ScoringEngine``      weighted rubric + letter grade.
    - ``ComplianceChecker`` CAN-SPAM / GDPR / SPF-DKIM-DMARC / spam-trigger checks.
    - ``FrameworkSelector``  chooses the smallest covering framework set.
    - ``ImprovementRoadmap`` effort x impact prioritisation.
    - ``KnowledgeBrain``     read / append the self-improving knowledge base.
"""
from .schemas import (
    CampaignBrief,
    Segment,
    EmailMessage,
    FrameworkChoice,
    DimensionScore,
    Scorecard,
    ComplianceFinding,
    RoadmapItem,
    CampaignReport,
    Evidence,
    Certainty,
)
from .intake import Intake
from .framework_selector import FrameworkSelector, FRAMEWORKS
from .scoring_engine import ScoringEngine, DIMENSIONS, letter_grade
from .compliance_check import ComplianceChecker
from .improvement_roadmap import ImprovementRoadmap
from .knowledge_brain import KnowledgeBrain
from .synthesizer import Synthesizer
from .challenge import Challenger
from .harness import Harness

__all__ = [
    "Harness",
    "Intake",
    "FrameworkSelector",
    "FRAMEWORKS",
    "ScoringEngine",
    "DIMENSIONS",
    "letter_grade",
    "ComplianceChecker",
    "ImprovementRoadmap",
    "KnowledgeBrain",
    "Challenger",
    "Synthesizer",
    "CampaignBrief",
    "Segment",
    "EmailMessage",
    "FrameworkChoice",
    "DimensionScore",
    "Scorecard",
    "ComplianceFinding",
    "RoadmapItem",
    "CampaignReport",
    "Evidence",
    "Certainty",
]

__version__ = "1.0.0"
