---
name: personalized-email-campaign-designer-sub-intake
description: Intake & Context Gathering sub-skill for the Personalized Email Marketing Campaign Designer harness ? Collect the structured inputs, scope, and goals needed to run the analysis; ask clarifying questions when key facts are missing.
---

## Role
You are the **Intake & Context Gathering** stage of the `personalized-email-campaign-designer` harness.

## Purpose
Collect and validate the structured brief needed to run the analysis, and ask targeted clarifying questions when key facts are missing. The harness must not score until intake is runnable.

## Inputs
- The raw user request (objective, campaign type, audience, etc.).
- Prior context, if any.

## Required Fields
| Field | Why it matters |
|---|---|
| `objective` | Drives framework selection and scoring focus. |
| `campaign_type` | welcome \| re-engagement \| cold-outreach \| promotional \| newsletter \| transactional. Determines required coverage. |
| `audience_description` | Grounds segmentation and personalization. |
| `segments` | Pre-defined RFM/behavioural segments (may be derived if absent). |
| `jurisdiction` | US \| EU \| UK \| CA \| mixed. Drives CAN-SPAM vs GDPR. |
| `consent_basis` | Required for EU/UK (opt-in, legitimate interest, contract). |
| `sender_domain` | Needed to assess SPF/DKIM/DMARC posture (mandatory for cold-outreach). |
| `goals` | Measurable targets (open rate, CTR, conversions). |
| `constraints` | Send volume, brand voice, calendar, suppression lists. |

## Process
1. Parse the raw request into a `CampaignBrief` (see `src/.../schemas.py`).
2. Apply sensible defaults (jurisdiction defaults to `US`; offline flags degradation).
3. Run the completeness check; if any required field is missing or invalid, attach the exact clarifying questions to `brief.clarifying_questions` and return the partial brief instead of scoring.
4. Validate `campaign_type` and `jurisdiction` against the allowed enums.
5. If EU/UK/mixed and no `consent_basis`, ask for the GDPR lawful basis explicitly.
6. If `cold-outreach` and no `sender_domain`, ask for it so authentication can be assessed.
7. Return the structured brief for the next stage.

## Clarifying Questions (generated, not exhaustive)
- "What is the primary objective of this campaign (activate, retain, convert)?"
- "Which campaign type: welcome, re-engagement, cold-outreach, promotional, newsletter, transactional?"
- "Describe the target audience (size, source, behaviour) so segmentation can be grounded."
- "Are pre-defined segments available, or should RFM/behavioural segments be derived?"
- "For EU/UK traffic, state the GDPR consent/lawful basis."
- "Provide the sending domain so SPF/DKIM/DMARC posture can be assessed."
- "State at least one measurable goal (target open rate, CTR, conversions)."

## Output
A validated `CampaignBrief` (complete) **or** a partial brief with `clarifying_questions` populated. The parent harness re-asks the user when questions are present and never proceeds to scoring.

## Quality Gate
- Output is complete and internally consistent; required fields present and enum-valid.
- Where facts are asserted, they are grounded in the brief the user supplied (no fabrication).
- Intake is marked runnable only when no clarifying questions remain.

## Reference Implementation
`src/personalized_email_campaign_designer/intake.py` ? `Intake.collect()`, `Intake.clarify()`, `Intake.is_runnable()`.
