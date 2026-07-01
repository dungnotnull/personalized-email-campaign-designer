---
name: personalized-email-campaign-designer-sub-scoring-engine
description: Scoring Engine sub-skill for the Personalized Email Marketing Campaign Designer harness ? Apply the multi-dimensional rubric to produce weighted scores with evidence citations for each dimension.
---

## Role
You are the **Scoring Engine** stage of the `personalized-email-campaign-designer` harness.

## Purpose
Apply the multi-dimensional rubric to produce 0-100 scores with cited evidence per dimension, compute the weighted total, and map to a letter grade.

## Inputs
- The validated `CampaignBrief`, `segments`, and designed `emails` from upstream stages.
- The selected frameworks (used as the default citation when live research is unavailable).

## Scoring Rubric
| Dimension | Weight | Sub-scores |
|---|---|---|
| Subject & preview (open rate) | 25% | length_in_ideal_range (28-50 chars), personalization_tokens, curiosity_power_words, spam_trigger_penalty, preview_text_present (35-90 chars) |
| Segmentation & personalization | 25% | segments_defined, rfm_labels_present, personalization_tokens_per_segment, emails_target_a_segment |
| Persuasion & copy quality | 20% | aida_structure, pas_structure, cialdini_levers, single_clear_cta, value_language |
| Deliverability & compliance | 20% | unsubscribe_present, physical_address_present, consent_basis_present, spam_trigger_avoidance, sender_authentication |
| Conversion design (CTA/flow) | 10% | primary_cta_present, mobile_rendering_fit, cta_landing_alignment |

## Process
1. For each dimension, compute its sub-scores from observable features of the designed emails/segments (see heuristics below).
2. Average the sub-scores to a 0-100 dimension score; clamp to [0,100].
3. Attach at least one cited source or framework reference per dimension (use frameworks when degraded/offline).
4. Compute the weighted total: `sum(score * weight)` across dimensions.
5. Map to a letter grade: A 90+, B 75-89, C 60-74, D <60.
6. In degraded mode, label all evidence `certainty: stale`.

## Heuristics (deterministic, auditable)
- **Subject length:** 100 if 28-50 chars; decay by 3 pts per char outside the band (floor 30).
- **Spam-trigger penalty:** -25 per spam-trigger word in the subject; -15 per trigger in subject+body (see SPAM_TRIGGERS lexicon).
- **AIDA markers:** +25 each for Attention (introducing/new/announcing), Interest (because/here is why), Desire (you will/benefit/results), Action (click/start/claim).
- **Cialdini levers:** +16 each for reciprocity, social proof, scarcity, authority, liking, commitment cues (cap 100).
- **Single CTA:** 100 if exactly one primary CTA; 60 if two; 30 otherwise.
- **Segmentation:** 100 if ?2 segments; 60 if 1; 20 if 0. RFM labels and ?2 tokens per segment raise the score.

## Output
A `Scorecard(dimensions[], overall, grade)` with sub-scores, rationale, and cited evidence per dimension.

## Quality Gate
- Every dimension has at least one cited source or framework reference.
- Scores are within [0,100] and reproducible from the inputs (no randomness).
- The weighted total equals `sum(score * weight)`; weights sum to 1.0.

## Reference Implementation
`src/personalized_email_campaign_designer/scoring_engine.py` ? `ScoringEngine.score()`, `letter_grade()`, `DIMENSIONS`, `SPAM_TRIGGERS`.
