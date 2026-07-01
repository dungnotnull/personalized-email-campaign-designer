# Personalized Email Marketing Campaign Designer (Skill #151)

Designs deeply personalized email campaigns using persuasion psychology,
segmentation, and anti-spam/deliverability standards. Part of the
`marketing-content-branding` skill cluster.

> Research-first, framework-grounded, compliance-gated. Runs fully offline
> ("degraded mode") and falls back to a self-improving local knowledge base
> (`SECOND-KNOWLEDGE-BRAIN.md`) when live research tools are unavailable.

## Why this skill

Email campaigns underperform from weak subject lines, poor segmentation, and
deliverability/compliance failures (spam folder, GDPR/CAN-SPAM violations).
This skill designs segmented, persuasive, compliant campaigns and scores
open/conversion potential on a multi-dimensional rubric.

## What's inside

```
.
+- skills/                      # Claude harness skill files (main.md + 5 sub-skills)
+- src/personalized_email_campaign_designer/   # production-grade Python implementation
|   +- schemas.py               # data models (CampaignBrief, Segment, EmailMessage, ...)
|   +- intake.py                # sub-intake: validate brief, ask clarifying questions
|   +- framework_selector.py    # sub-framework-selector: smallest covering framework set
|   +- scoring_engine.py        # sub-scoring-engine: weighted rubric + letter grade
|   +- compliance_check.py      # sub-compliance-check: CAN-SPAM / GDPR / SPF-DKIM-DMARC / spam
|   +- improvement_roadmap.py    # sub-improvement-roadmap: effort x impact prioritisation
|   +- challenge.py             # devil's-advocate assumption review
|   +- knowledge_brain.py       # read/append SECOND-KNOWLEDGE-BRAIN.md
|   +- synthesizer.py           # render the professional report
|   +- harness.py               # end-to-end orchestrator (mirrors skills/main.md)
|   +- cli.py / __main__.py     # `python -m personalized_email_campaign_designer`
+- tools/knowledge_updater.py   # weekly crawl pipeline (ArXiv API + crawl4ai optional)
+- tests/test_harness.py        # deterministic pytest suite (5 scenarios, offline)
+- SECOND-KNOWLEDGE-BRAIN.md    # self-improving knowledge base
+- PROJECT-detail.md            # full technical spec
+- PROJECT-DEVELOPMENT-PHASE-TRACKING.md
```

## Evaluation frameworks (citable)

| Framework / Standard | Role |
|---|---|
| AIDA & PAS | Structure subject, body and CTA persuasion. |
| Cialdini's six principles | Reciprocity, commitment, social proof, authority, liking, scarcity. |
| RFM segmentation | Recency-Frequency-Monetary audience targeting. |
| SPF / DKIM / DMARC | Inbox placement and sender reputation (RFC 7208/6376/7489). |
| CAN-SPAM & GDPR/ePrivacy | Legal compliance for commercial email. |

## Scoring rubric

| Dimension | Weight | What is assessed |
|---|---|---|
| Subject & preview (open rate) | 25% | curiosity, clarity, length, personalization tokens |
| Segmentation & personalization | 25% | RFM/behavioural targeting and dynamic content |
| Persuasion & copy quality | 20% | AIDA/PAS structure, value, single clear CTA |
| Deliverability & compliance | 20% | authentication, unsubscribe, consent, spam-trigger avoidance |
| Conversion design (CTA/flow) | 10% | CTA placement, landing alignment, mobile rendering |

Each dimension is scored 0-100 with cited evidence; the weighted total maps to a
letter grade: **A** 90+, **B** 75-89, **C** 60-74, **D** <60.

## Quick start

```bash
pip install -e .[dev]
pytest -q                                   # deterministic, offline suite

# Run a brief (intake only)
python -m personalized_email_campaign_designer --brief examples/welcome.json

# Run a full design (brief + segments + emails) and write the report
python -m personalized_email_campaign_designer --design examples/welcome.json -o report.md

# Grow the knowledge base (weekly cron recommended)
python tools/knowledge_updater.py --dry-run
```

### Brief / design JSON shape

```json
{
  "objective": "Activate new signups in the first 14 days",
  "campaign_type": "welcome",
  "audience_description": "New free-trial signups",
  "jurisdiction": "US",
  "sender_domain": "mail.example.com",
  "goals": ["reach 40% trial-to-paid"],
  "offline": true,
  "segments": [
    {"name": "New-Trial", "rfm_label": "New", "personalization_tokens": ["first_name"]}
  ],
  "emails": [
    {
      "position": 1, "name": "Welcome + setup", "segment": "New-Trial",
      "subject_line": "{{first_name}}, welcome - let's get you set up",
      "preview_text": "Your workspace is ready. 3 steps to your first project.",
      "body": "Hi {{first_name}}, welcome aboard. Here is why teams choose us. Discover the 3-step setup. Start your first project today.",
      "cta_primary": "Start setup"
    }
  ]
}
```

## Quality gates (must all pass before final output)

- Every score cites at least one source or the chosen framework.
- Challenge stage completed; key assumptions tested.
- Roadmap items prioritised by effort and impact and traceable to findings.
- Limitations and evidence certainty are stated explicitly.
- Compliance check passed against applicable laws/standards before output;
  items needing legal/professional review are flagged.

## License

MIT - see [LICENSE](LICENSE).
