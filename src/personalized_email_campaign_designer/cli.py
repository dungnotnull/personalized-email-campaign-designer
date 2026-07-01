# -*- coding: utf-8 -*-
"""Command-line interface for the Personalized Email Campaign Designer.

Examples
--------
    # Run a brief file and print the markdown report
    python -m personalized_email_campaign_designer --brief brief.json

    # Read brief from stdin, write report to file
    cat brief.json | python -m personalized_email_campaign_designer -o report.md

    # Score an already-designed campaign (brief + segments + emails in one JSON)
    python -m personalized_email_campaign_designer --design design.json -o report.md

The brief JSON shape mirrors ``CampaignBrief``; a design JSON additionally embeds
``segments`` and ``emails`` arrays (see schemas.py for field names).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from typing import List, Tuple

from .harness import Harness
from .schemas import CampaignBrief, EmailMessage, Segment


_EMAIL_DEFAULTS = {
    "position": 1, "name": "", "segment": "", "subject_line": "",
    "preview_text": "", "body": "", "cta_primary": "", "cta_secondary": "",
    "send_delay_days": 0, "has_unsubscribe": True, "has_physical_address": True,
    "has_consent_basis": True,
}


def _build_brief(data: dict) -> Tuple[CampaignBrief, List[Segment], List[EmailMessage]]:
    brief = CampaignBrief(
        objective=data.get("objective", ""),
        campaign_type=data.get("campaign_type", ""),
        audience_description=data.get("audience_description", ""),
        constraints=data.get("constraints", []),
        goals=data.get("goals", []),
        jurisdiction=data.get("jurisdiction", "US"),
        consent_basis=data.get("consent_basis"),
        sender_domain=data.get("sender_domain"),
        offline=bool(data.get("offline", False)),
        notes=data.get("notes", ""),
    )
    segments: List[Segment] = []
    for s in data.get("segments", []) or []:
        segments.append(Segment(
            name=s.get("name", ""), description=s.get("description", ""),
            recency_days=s.get("recency_days"), frequency=s.get("frequency"),
            monetary=s.get("monetary"), rfm_label=s.get("rfm_label"),
            size=s.get("size"), personalization_tokens=s.get("personalization_tokens", []),
        ))
    emails: List[EmailMessage] = []
    for i, e in enumerate(data.get("emails", []) or []):
        merged = dict(_EMAIL_DEFAULTS)
        merged.update(e)
        merged.setdefault("position", i + 1)
        emails.append(EmailMessage(**merged))
    return brief, segments, emails


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="personalized-email-campaign-designer",
        description="Design and score a personalized, compliant email campaign.")
    src = parser.add_mutually_exclusive_group()
    src.add_argument("--brief", help="Path to a brief JSON file (intake only).")
    src.add_argument("--design", help="Path to a design JSON file (brief + segments + emails).")
    parser.add_argument("-o", "--output", help="Write the markdown report to this path; default stdout.")
    parser.add_argument("--brain", help="Path to SECOND-KNOWLEDGE-BRAIN.md (optional).")
    parser.add_argument("--json", action="store_true", help="Emit the report as JSON instead of markdown.")
    args = parser.parse_args(argv)

    if args.brief or args.design:
        with open(args.brief or args.design, "r", encoding="utf-8-sig") as f:
            data = json.load(f)
    else:
        data = json.load(sys.stdin)

    brief, segments, emails = _build_brief(data)
    harness = Harness(brain_path=args.brain)
    if emails:
        report = harness.run_with_design(brief, segments, emails)
    else:
        report = harness.run(data)

    if args.json:
        out = json.dumps(report.to_dict(), indent=2, default=str)
    else:
        out = harness.synthesizer.render(report)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out)
        print(f"[ok] report written to {args.output} (gates_passed={report.gates_passed}, grade={report.scorecard.grade})", file=sys.stderr)
    else:
        print(out)
    return 0 if report.gates_passed else 2


if __name__ == "__main__":
    sys.exit(main())
