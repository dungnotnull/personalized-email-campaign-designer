# PROJECT-detail.md ? Personalized Email Marketing Campaign Designer (Skill #151)

## Executive Summary
Designs deeply personalized email campaigns using persuasion psychology, segmentation, and anti-spam/deliverability standards. This skill is a full Claude harness in the **marketing-content-branding** cluster. It runs a research-first, framework-grounded workflow that scores the subject against named world-renowned methodologies and returns a prioritized improvement roadmap, while continuously updating its knowledge base. A production-grade, dependency-light Python implementation (`src/personalized_email_campaign_designer/`) mirrors the harness 1:1 and ships as a CLI + pytest suite.

## Problem Statement
Email campaigns underperform from weak subject lines, poor segmentation, and deliverability/compliance failures (spam folder, GDPR/CAN-SPAM violations). This skill designs segmented, persuasive, compliant campaigns and scores open/conversion potential.

## Target Users & Use Cases
Practitioners, reviewers, and decision-makers who need an expert-grade, evidence-based assessment. Trigger examples:
1. **Welcome series** ? "Design a 5-email onboarding sequence" ? segments, sequences, scores, checks compliance.
2. **Re-engagement** ? "Win back inactive subscribers" ? RFM segmentation, copy, opt-out/consent verification.
3. **Cold outreach** ? "B2B cold email campaign" ? personalized copy, CAN-SPAM/GDPR limits flagged.
4. **Subject line test** ? "Give me 10 subject lines + scores" ? open-rate + spam-trigger scoring.
5. **Degraded mode** ? "Design offline" ? fallback to brain benchmarks, flags deliverability data stale.

## Harness Architecture
```
/personalized-email-campaign-designer (main.md)
   ??? sub-intake .................... Intake & Context Gathering
   ??? sub-framework-selector ....... Evaluation Framework Selector
   ??? [research] WebSearch/WebFetch + SECOND-KNOWLEDGE-BRAIN (degrades gracefully)
   ??? sub-scoring-engine ............ Scoring Engine
   ??? [challenge] devil's-advocate assumption review
   ??? sub-compliance-check .......... Compliance Check (hard gate)
   ??? sub-improvement-roadmap ....... Improvement Roadmap
   ??? synthesize ................... professional deliverable + quality gates
```

## Evaluation Frameworks (World-Renowned, Citable)
| Framework / Standard | Role in this skill | Citation |
|---|---|---|
| AIDA & PAS copy frameworks | Structure subject, body, and CTA persuasion. | Lewis (1898) AIDA; Kennedy/Dan Kennedy PAS copywriting |
| Cialdini's principles of influence | Reciprocity, commitment, social proof, authority, liking, scarcity in copy. | Cialdini, R. B. (1984/2021). *Influence: The Psychology of Persuasion.* |
| RFM segmentation | Recency-Frequency-Monetary audience targeting. | Hughes, A. M. (1996). *The Complete Database Marketer.* |
| Deliverability standards (SPF/DKIM/DMARC) | Inbox placement and sender reputation. | RFC 7208 (SPF), RFC 6376 (DKIM), RFC 7489 (DMARC) |
| CAN-SPAM & GDPR consent rules | Legal compliance for commercial email. | US CAN-SPAM Act (2003, FTC); GDPR (EU 2016/679); ePrivacy Directive 2002/58/EC |

## Scoring Model
| Dimension | Weight | What is assessed |
|---|---|---|
| Subject & preview (open rate) | 25% | curiosity, clarity, length, personalization tokens |
| Segmentation & personalization | 25% | RFM/behavioral targeting and dynamic content |
| Persuasion & copy quality | 20% | AIDA/PAS structure, value, single clear CTA |
| Deliverability & compliance | 20% | authentication, unsubscribe, consent, spam-trigger avoidance |
| Conversion design (CTA/flow) | 10% | CTA placement, landing alignment, mobile rendering |

Each dimension is scored 0-100 with cited evidence; the weighted total yields an overall grade (A: 90+, B: 75-89, C: 60-74, D: <60).

## Evidence Hierarchy
Systematic Review > Meta-Analysis > RCT > Cohort > Expert Opinion > Blog. Prefer primary standards documents (RFCs, statutes) and peer-reviewed sources over secondary blogs. In degraded mode, cite the chosen framework as the default and label certainty `stale`.

## Skill File Format Specification
- Frontmatter: `name`, `description`.
- Required sections: Role & Persona, Workflow (Harness Flow), Sub-skills Available, Tools, Output Format, Quality Gates.

## E2E Execution Flow
1. Parse user request; if inputs are insufficient, `sub-intake` asks targeted questions and blocks scoring.
2. `sub-framework-selector` picks the smallest covering framework set and justifies it.
3. Research stage gathers highest-tier evidence; degrade gracefully to SECOND-KNOWLEDGE-BRAIN if offline.
4. `sub-scoring-engine` scores each dimension with citations and computes the weighted grade.
5. Challenge stage stress-tests conclusions and assigns overall certainty.
6. `sub-compliance-check` verifies output against applicable laws/standards (hard gate).
7. `sub-improvement-roadmap` produces ranked actions traceable to findings.
8. Synthesize deliverable; run Quality Gates; present.

**Error handling:** missing inputs ? ask; conflicting evidence ? present both and grade certainty; tool failure ? fallback + explicit limitation notice; compliance fail ? block release.

## SECOND-KNOWLEDGE-BRAIN Integration
- Sources: https://www.litmus.com, https://mailchimp.com/resources, https://www.campaignmonitor.com, https://gdpr.eu.
- ArXiv categories: cs.IR (queried via the ArXiv export API).
- Crawl queries: email marketing benchmarks open rate; email deliverability DMARC best practice; persuasion copywriting email conversion; GDPR CAN-SPAM email compliance.
- Append format: dated entries with Title, Authors, Year, Venue, DOI/URL, key finding, relevance score; dedup by URL/DOI hash.

## Supporting Tools Spec
`tools/knowledge_updater.py`: inputs = source list + queries; outputs = appended SECOND-KNOWLEDGE-BRAIN entries; schedule = weekly cron; dedup by URL/DOI hash; supports `--dry-run`, `--max`, `--no-web`, optional crawl4ai.

## Quality Gates (must all pass before final output)
- Every score cites at least one source or the chosen framework.
- Challenge stage completed; key assumptions tested.
- Roadmap items are prioritized by effort and impact and traceable to findings.
- Limitations and evidence certainty are stated explicitly.
- Compliance check passed against applicable laws/standards before release.

## Test Scenarios
1. **Welcome series** ? segments, sequences, scores, checks compliance.
2. **Re-engagement** ? RFM, copy, opt-out/consent.
3. **Cold outreach** ? personalized copy, CAN-SPAM/GDPR limits.
4. **Subject line test** ? open-rate + spam-trigger scoring.
5. **Degraded mode** ? fallback to brain benchmarks, stale flag.

## Key Design Decisions
1. Framework-grounded scoring (no ad-hoc criteria).
2. Research-first with graceful degradation to the local knowledge brain.
3. Mandatory challenge stage to counter confirmation bias.
4. Compliance check standard quality gates enforced before delivery (hard gate).
5. Self-improving knowledge base via weekly crawl.
6. A deterministic Python implementation makes the rubric reproducible and auditable, and CI-testable offline.

## Reference Implementation
`src/personalized_email_campaign_designer/` ? `Harness`, `Intake`, `FrameworkSelector`, `ScoringEngine`, `ComplianceChecker`, `ImprovementRoadmap`, `Challenger`, `KnowledgeBrain`, `Synthesizer`, plus CLI (`python -m personalized_email_campaign_designer`). Tested by `tests/test_harness.py` (11 tests, all scenarios offline).
