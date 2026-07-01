# CLAUDE.md ? Personalized Email Marketing Campaign Designer (Skill #151)

**Slug:** `personalized-email-campaign-designer`  ?  **Cluster:** `marketing-content-branding`  ?  **Source idea:** 151  ?  **Phase:** Built (v1.0.0)

## Tagline
Designs deeply personalized email campaigns using persuasion psychology, segmentation, and anti-spam/deliverability standards.

## Problem This Skill Solves
Email campaigns underperform from weak subject lines, poor segmentation, and deliverability/compliance failures (spam folder, GDPR/CAN-SPAM violations). This skill designs segmented, persuasive, compliant campaigns and scores open/conversion potential.

## Harness Flow Summary
1. **Intake** (`sub-intake`) ? gather structured inputs, scope, goals.
2. **Framework selection** (`sub-framework-selector`) ? choose named world-renowned framework(s).
3. **Research** (WebSearch/WebFetch + SECOND-KNOWLEDGE-BRAIN) ? gather highest-tier evidence; degrade gracefully.
4. **Scoring** (`sub-scoring-engine`) ? multi-dimensional weighted scores with citations.
5. **Challenge** ? devil's-advocate review of assumptions and weak evidence.
6. **Compliance check** (`sub-compliance-check`) ? verify against laws/standards (hard gate).
7. **Roadmap** (`sub-improvement-roadmap`) ? prioritized effort/impact recommendations.
8. **Synthesize** ? assemble the professional deliverable; pass Quality Gates.

## Gates
- **Compliance gate:** `sub-compliance-check` MUST run before final output (regulated content). Any `fail` blocks release until remediated or explicitly flagged for professional/legal review.

## Sub-skills
- `skills/sub-intake.md` ? Intake & Context Gathering.
- `skills/sub-framework-selector.md` ? Evaluation Framework Selector.
- `skills/sub-scoring-engine.md` ? Scoring Engine.
- `skills/sub-compliance-check.md` ? Compliance Check.
- `skills/sub-improvement-roadmap.md` ? Improvement Roadmap.

## Tools Required
- `WebSearch`, `WebFetch` ? live evidence and standards updates.
- `Read`, `Write` ? load knowledge base, emit deliverables.
- `Bash` ? run `tools/knowledge_updater.py` and the reference implementation.
- Skill tool ? invoke sub-skills in sequence.

## Reference Implementation
A production-grade, dependency-light Python package mirrors the harness 1:1 in
`src/personalized_email_campaign_designer/` (Python 3.9+, stdlib only). Runnable
as a CLI:

```bash
python -m personalized_email_campaign_designer --design examples/welcome.json -o report.md
pytest -q   # deterministic, offline test suite (tests/test_harness.py)
```

The Python package is the authoritative scorer/compliance engine; the markdown
skill files are the human-readable contract that mirrors it.

## Knowledge Sources
- ArXiv: cs.IR (queried via the ArXiv export API in `tools/knowledge_updater.py`).
- Authoritative domain sources:
  - https://www.litmus.com
  - https://mailchimp.com/resources
  - https://www.campaignmonitor.com
  - https://gdpr.eu
- Crawl queries: email marketing benchmarks open rate; email deliverability DMARC best practice; persuasion copywriting email conversion; GDPR CAN-SPAM email compliance.

## Supporting Tools
- `tools/knowledge_updater.py` ? ArXiv API (stdlib urllib) + optional crawl4ai pipeline that grows `SECOND-KNOWLEDGE-BRAIN.md` (weekly cron recommended). Supports `--dry-run`, `--max`, `--no-web`.

## Cluster Cross-References (Phase 5 ? reuse manifest)
This skill is part of the `marketing-content-branding` cluster. The following
sub-skills are intentionally self-contained so sibling skills can compose them:

| Sub-skill | Reusable as | Consumer examples (sibling skills) |
|---|---|---|
| `sub-intake` | Generic marketing-campaign intake prompt | `ad-copy-designer`, `landing-page-optimizer`, `audience-segmenter` |
| `sub-framework-selector` | Named-framework selector for any persuasion task | `ad-copy-designer`, `value-proposition-designer` |
| `sub-scoring-engine` | Multi-dimensional weighted scorer + letter grade | `landing-page-optimizer`, `ad-copy-designer` |
| `sub-compliance-check` | CAN-SPAM/GDPR/deliverability audit | `sms-marketing-designer`, `push-notification-designer` |
| `sub-improvement-roadmap` | effort ? impact prioritisation engine | any scored skill in the cluster |

Sibling skills importing the Python package should depend on
`personalized_email_campaign_designer` and reuse `FrameworkSelector`,
`ScoringEngine`, `ComplianceChecker`, and `ImprovementRoadmap` rather than
re-implementing them.

## Active Development Tasks
- [x] Scaffold full deliverable set.
- [x] Define 5 sub-skills (production-grade specs).
- [x] Author `skills/main.md` with stage order + hard compliance gate.
- [x] Implement reference Python harness (`src/personalized_email_campaign_designer/`).
- [x] Implement `tools/knowledge_updater.py` (ArXiv API + optional crawl4ai + dedup + dry-run).
- [x] Add deterministic pytest suite (5 scenarios, offline/degraded).
- [x] Add CLI + pyproject + README + LICENSE (opensource-ready).
- [x] Cross-reference the `marketing-content-branding` cluster (Phase 5).
- [ ] Expand SECOND-KNOWLEDGE-BRAIN with first live crawl (run in production stage to save resources).

## Related Root Docs
- `PROJECT-detail.md` ? full technical spec.
- `PROJECT-DEVELOPMENT-PHASE-TRACKING.md` ? phase roadmap.
- `SECOND-KNOWLEDGE-BRAIN.md` ? self-improving knowledge base.
