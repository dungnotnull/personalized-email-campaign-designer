# Test Scenarios ? Personalized Email Marketing Campaign Designer (Skill #151)

These scenarios validate the harness end-to-end: stage order, framework grounding,
scoring with citations, gates, roadmap, and graceful degradation. They are
implemented deterministically and offline in `tests/test_harness.py` so they run
in CI without network, models, or live research.

## Scenario 1: Welcome series
- **User input:** "Design a 5-email onboarding sequence"
- **Brief:** campaign_type=`welcome`, jurisdiction=`US`, sender_domain set, 1 segment (`New-Trial`), 2 emails with `{{first_name}}` tokens.
- **Expected behavior:** Skill segments, sequences, scores, checks compliance.
- **Assertions:**
  - Correct stage order (intake ? framework ? score ? challenge ? compliance ? roadmap ? synthesize).
  - AIDA and CAN-SPAM frameworks selected and justified.
  - Each dimension score cites a source/framework.
  - Roadmap non-empty and prioritized.
  - `gates_passed=True`; no compliance `fail`.
  - Report markdown contains "Grade" and "Improvement Roadmap".

## Scenario 2: Re-engagement
- **User input:** "Win back inactive subscribers"
- **Brief:** campaign_type=`re-engagement`, jurisdiction=`US`, 2 RFM segments (`Champions-Lapsed`, `At-Risk`), 1 email with unsubscribe + physical address.
- **Expected behavior:** RFM segmentation, copy, opt-out/consent verification.
- **Assertions:**
  - RFM framework selected.
  - Segmentation & personalization score ? 60.
  - `gates_passed=True`; email carries `has_unsubscribe` and `has_physical_address`.

## Scenario 3: Cold outreach
- **User input:** "B2B cold email campaign"
- **Brief:** campaign_type=`cold-outreach`, jurisdiction=`US`, sender_domain set, 1 segment, 1 email.
- **Expected behavior:** Personalized copy, CAN-SPAM/GDPR limits flagged.
- **Assertions:**
  - CAN-SPAM and SPF-DKIM-DMARC frameworks selected.
  - `gates_passed=True` for a compliant draft.
- **Negative case:** an email with `has_unsubscribe=False` and `has_physical_address=False` must produce a compliance `fail`, block release (`gates_passed=False`).

## Scenario 4: Subject line test
- **User input:** "Give me 10 subject lines + scores"
- **Brief:** campaign_type=`promotional`, 10 emails with mixed subject lines (incl. one spam-trigger-heavy: "FREE money now!!! click here").
- **Expected behavior:** Open-rate + spam-trigger scoring.
- **Assertions:**
  - Subject & preview dimension score in [0,100].
  - A compliance `warn` with rule containing "spam-trigger" is produced for the spammy line.

## Scenario 5: Degraded mode
- **User input:** "Design offline"
- **Brief:** campaign_type=`newsletter`, jurisdiction=`US`, `offline=True`; a tiny local brain fixture is written.
- **Expected behavior:** Fallback to brain benchmarks, flags deliverability data stale.
- **Assertions:**
  - `report.degraded is True`.
  - Limitations mention "stale" or "offline".
  - Challenge `certainty_overall == "stale"`.

## Unit-level assertions
- Rubric weights sum to 1.0.
- `letter_grade` thresholds: 95?A, 89?B, 75?B, 60?C, 59?D.
- Framework selector picks the smallest covering set; GDPR (not CAN-SPAM) for EU jurisdiction.
- Intake attaches clarifying questions and blocks when the brief is incomplete.
- `DimensionScore` raises `ValueError` for scores outside [0,100].

## Regression Notes
- Add real user runs here as regression cases.
- Verify `tools/knowledge_updater.py --dry-run` appends well-formed, deduplicated entries (run in production stage).
- Verify the compliance check blocks release on a non-compliant draft (Scenario 3 negative case).

## How to run
```bash
pip install -e .[dev]
pytest -q
```
