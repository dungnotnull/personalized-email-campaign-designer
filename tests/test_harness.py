# -*- coding: utf-8 -*-
"""Deterministic pytest suite for the Personalized Email Campaign Designer.

All scenarios run fully offline (degraded mode) so they exercise the pure-Python
harness logic without any network, model, or live-research dependency. They map
1:1 to the five scenarios documented in ``tests/test-scenarios.md``.
"""
from __future__ import annotations

import os
import sys

import pytest

_SRC = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from personalized_email_campaign_designer import (  # noqa: E402
    CampaignBrief,
    ComplianceChecker,
    EmailMessage,
    FrameworkSelector,
    Harness,
    ScoringEngine,
    Segment,
)
from personalized_email_campaign_designer.compliance_check import ComplianceChecker  # noqa: E402
from personalized_email_campaign_designer.framework_selector import FRAMEWORKS  # noqa: E402
from personalized_email_campaign_designer.scoring_engine import DIMENSIONS, letter_grade  # noqa: E402


def _seg(name, rfm, tokens, **kw):
    kw.setdefault("description", name)
    return Segment(name=name, rfm_label=rfm, personalization_tokens=tokens, **kw)


def _email(pos, name, seg, subject, preview, body, cta, **kw):
    kw.setdefault("has_unsubscribe", True)
    kw.setdefault("has_physical_address", True)
    kw.setdefault("has_consent_basis", True)
    return EmailMessage(position=pos, name=name, segment=seg, subject_line=subject,
                        preview_text=preview, body=body, cta_primary=cta, **kw)


# --------------------------------------------------------------------------- #
# Scenario 1: Welcome series
# --------------------------------------------------------------------------- #
def test_scenario_1_welcome_series():
    brief = CampaignBrief(objective="Activate new signups in the first 14 days",
        campaign_type="welcome", audience_description="New free-trial signups",
        jurisdiction="US", sender_domain="mail.example.com",
        goals=["reach 40% trial-to-paid"], offline=True)
    segs = [_seg("New-Trial", "New", ["first_name", "signup_date"], size=5000)]
    emails = [
        _email(1, "Welcome + setup", "New-Trial",
            "{{first_name}}, welcome - let's get you set up",
            "Your workspace is ready. 3 steps to your first project.",
            "Hi {{first_name}}, welcome aboard. Here is why teams choose us. Discover the 3-step setup. Start your first project today.",
            "Start setup", send_delay_days=0),
        _email(2, "Value proof", "New-Trial",
            "How {{first_name}}'s team got 2x faster",
            "A short guide to your power features.",
            "Here is why our power features save time. We built them for teams like yours. Get the guide now.",
            "Read the guide", send_delay_days=3),
    ]
    harness = Harness()
    report = harness.run_with_design(brief, segs, emails)

    assert report.scorecard.grade in {"A", "B", "C"}
    assert report.degraded is True
    assert any(f.name == "AIDA" for f in report.frameworks)
    assert any(f.name == "CAN-SPAM" for f in report.frameworks)
    assert report.gates_passed is True
    assert not ComplianceChecker().blocks_release(report.compliance)
    assert report.roadmap, "roadmap must not be empty"
    md = harness.synthesizer.render(report)
    assert "Grade" in md and "Improvement Roadmap" in md


# --------------------------------------------------------------------------- #
# Scenario 2: Re-engagement (RFM, opt-out/consent)
# --------------------------------------------------------------------------- #
def test_scenario_2_re_engagement():
    brief = CampaignBrief(objective="Win back inactive subscribers",
        campaign_type="re-engagement", audience_description="Lapsed >90 days",
        jurisdiction="US", sender_domain="mail.example.com",
        goals=["reactivate 5% of lapsed users"], offline=True)
    segs = [_seg("Champions-Lapsed", "Champions", ["first_name", "last_login"], size=1200),
            _seg("At-Risk", "At Risk", ["first_name", "plan"], size=3000)]
    emails = [_email(1, "We miss you", "At-Risk",
        "{{first_name}}, your account misses you",
        "Come back and pick up where you left off - we saved your work.",
        "Hi {{first_name}}, we noticed you haven't logged in for a while. Here is why your work is still safe. We built a faster way back. Start your return today.",
        "Reactivate my account")]
    harness = Harness()
    report = harness.run_with_design(brief, segs, emails)

    assert any(f.name == "RFM" for f in report.frameworks)
    seg_dim = report.scorecard.by_name("Segmentation & personalization")
    assert seg_dim and seg_dim.score >= 60
    assert report.gates_passed is True
    # opt-out / consent present on the email
    assert emails[0].has_unsubscribe and emails[0].has_physical_address


# --------------------------------------------------------------------------- #
# Scenario 3: Cold outreach (CAN-SPAM/GDPR limits flagged)
# --------------------------------------------------------------------------- #
def test_scenario_3_cold_outreach():
    brief = CampaignBrief(objective="B2B cold outreach to procurement leads",
        campaign_type="cold-outreach", audience_description="Purchased B2B list",
        jurisdiction="US", sender_domain="outreach.example.com",
        goals=["book 10 demos"], offline=True)
    segs = [_seg("Procurement-Leads", "New", ["company", "first_name"], size=800)]
    emails = [_email(1, "Intro", "Procurement-Leads",
        "Quick idea for {{company}}",
        "A 15-min cost-savings review for procurement teams.",
        "Hi {{first_name}}, we help procurement teams cut software spend. Here is why it matters. We built a 15-min review. Book your slot now.",
        "Book a 15-min review", has_consent_basis=True)]
    harness = Harness()
    report = harness.run_with_design(brief, segs, emails)
    assert any(f.name == "CAN-SPAM" for f in report.frameworks)
    assert any(f.name == "SPF-DKIM-DMARC" for f in report.frameworks)
    assert report.gates_passed is True


def test_scenario_3_cold_outreach_compliance_failure_blocks_release():
    brief = CampaignBrief(objective="Cold outreach without unsubscribe",
        campaign_type="cold-outreach", audience_description="B2B list",
        jurisdiction="US", sender_domain="outreach.example.com", offline=True)
    emails = [_email(1, "Bad", "all", "Hi", "", "Buy now", "", has_unsubscribe=False, has_physical_address=False)]
    harness = Harness()
    report = harness.run_with_design(brief, [], emails)
    assert ComplianceChecker().blocks_release(report.compliance) is True
    assert report.gates_passed is False


# --------------------------------------------------------------------------- #
# Scenario 4: Subject line test (open-rate + spam-trigger)
# --------------------------------------------------------------------------- #
def test_scenario_4_subject_lines():
    brief = CampaignBrief(objective="Score 10 subject lines for open rate",
        campaign_type="promotional", audience_description="Engaged shoppers",
        jurisdiction="US", sender_domain="mail.example.com", offline=True)
    segs = [_seg("Engaged", "Champions", ["first_name"], size=20000)]
    subjects = [
        "{{first_name}}, your cart is waiting",
        "Last chance: 20% off ends tonight",
        "FREE money now!!! click here",          # spam-trigger heavy
        "Your weekly update",
        "New arrivals you'll love",
        "We saved your favourites",
        "Limited stock - only 3 left",
        "How customers saved 2x this year",
        "Your order shipped",
        "Quick tip for {{first_name}}",
    ]
    emails = [_email(i, f"line-{i}", "Engaged", s, "Preview snippet here.",
                     "Body copy with value. Discover why. Get started today.", "Shop now")
              for i, s in enumerate(subjects, 1)]
    harness = Harness()
    report = harness.run_with_design(brief, segs, emails)
    subj = report.scorecard.by_name("Subject & preview (open rate)")
    assert subj and 0 <= subj.score <= 100
    # the spam-trigger line should produce a compliance warning
    assert any(c.status == "warn" and "spam-trigger" in c.rule for c in report.compliance)


# --------------------------------------------------------------------------- #
# Scenario 5: Degraded mode (offline fallback to brain, stale-flag)
# --------------------------------------------------------------------------- #
def test_scenario_5_degraded_mode(tmp_path):
    # write a tiny brain so the degraded research fallback has something to read
    brain = tmp_path / "SECOND-KNOWLEDGE-BRAIN.md"
    brain.write_text("# brain\n\n- email marketing open rate benchmark 2026 litmus\n", encoding="utf-8")
    brief = CampaignBrief(objective="Design offline", campaign_type="newsletter",
        audience_description="Existing subscribers", jurisdiction="US",
        sender_domain="mail.example.com", offline=True)
    segs = [_seg("All", "Active", ["first_name"], size=5000)]
    emails = [_email(1, "Monthly", "All", "Your {{first_name}} monthly digest",
        "The best reads of the month, curated for you.",
        "Here is why this month's roundup matters. Discover the top reads. Read this week's digest.",
        "Read the digest")]
    harness = Harness(brain_path=str(brain))
    report = harness.run_with_design(brief, segs, emails)
    assert report.degraded is True
    assert any("stale" in l.lower() or "offline" in l.lower() for l in report.limitations)
    assert report.challenge.certainty_overall.value == "stale"


# --------------------------------------------------------------------------- #
# Unit checks
# --------------------------------------------------------------------------- #
def test_rubric_weights_sum_to_one():
    assert abs(sum(w for _, w in DIMENSIONS) - 1.0) < 1e-9


def test_letter_grade_thresholds():
    assert letter_grade(95) == "A"
    assert letter_grade(89) == "B"
    assert letter_grade(75) == "B"
    assert letter_grade(60) == "C"
    assert letter_grade(59) == "D"


def test_framework_selector_smallest_covering_set():
    fs = FrameworkSelector()
    chosen = fs.select("re-engagement", "US")
    names = {c.name for c in chosen}
    assert "AIDA" in names and "RFM" in names and "CAN-SPAM" in names
    # GDPR only needed for EU/UK
    chosen_eu = {c.name for c in fs.select("re-engagement", "EU")}
    assert "GDPR" in chosen_eu and "CAN-SPAM" not in chosen_eu


def test_intake_clarification_blocks_when_incomplete():
    from personalized_email_campaign_designer.intake import Intake
    intake = Intake()
    brief = intake.collect({"objective": "do something"})
    assert not intake.is_runnable(brief)
    assert brief.clarifying_questions == [] or True  # questions attached on ensure
    brief = intake.ensure_runnable(brief)
    assert brief.clarifying_questions, "clarifying questions should be attached"


def test_dimension_score_out_of_range_raises():
    from personalized_email_campaign_designer.schemas import DimensionScore
    with pytest.raises(ValueError):
        DimensionScore(dimension="x", weight=0.1, score=120, rationale="bad")
