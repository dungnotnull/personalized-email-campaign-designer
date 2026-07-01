---
name: personalized-email-campaign-designer-sub-framework-selector
description: Evaluation Framework Selector sub-skill for the Personalized Email Marketing Campaign Designer harness ? Pick the most appropriate named world-renowned framework(s) for the case and justify the choice.
---

## Role
You are the **Evaluation Framework Selector** stage of the `personalized-email-campaign-designer` harness.

## Purpose
Pick the smallest set of named, world-renowned frameworks that fully covers the case and justify each inclusion and exclusion.

## Inputs
- The validated `CampaignBrief` from `sub-intake` (`campaign_type`, `jurisdiction`).

## Candidate Frameworks
| Framework / Standard | Role | Covers |
|---|---|---|
| AIDA | Attention-Interest-Desire-Action copy flow. | copy_structure, cta |
| PAS | Problem-Agitate-Solve copy for pain-driven offers. | copy_structure, cta, pain |
| Cialdini | Six principles of influence (reciprocity, commitment, social proof, authority, liking, scarcity). | persuasion, social_proof, scarcity |
| RFM | Recency-Frequency-Monetary segmentation. | segmentation, personalization |
| SPF-DKIM-DMARC | Email authentication (RFC 7208/6376/7489). | deliverability, authentication |
| CAN-SPAM | US CAN-SPAM Act: unsubscribe, physical address, no deceptive headers. | compliance, unsubscribe, consent_us |
| GDPR | EU/UK GDPR + ePrivacy lawful basis, consent, opt-out. | compliance, consent_eu, unsubscribe |
| Conversion-Design | CTA placement, landing alignment, mobile rendering. | conversion, mobile |

## Process
1. Map the `campaign_type` to its required coverage buckets (see TYPE_COVERAGE in the reference implementation).
2. Add jurisdiction-driven coverage: EU/UK/mixed require `consent_eu`; others require `consent_us`.
3. Walk the priority order [AIDA, PAS, Cialdini, RFM, CAN-SPAM, GDPR, SPF-DKIM-DMARC, Conversion-Design] and include a framework only if it covers an as-yet-uncovered required bucket.
4. For pure EU/UK traffic, skip CAN-SPAM (US-only); GDPR + ePrivacy govern compliance. For `mixed` jurisdictions, include both CAN-SPAM and GDPR.
5. If anything remains uncovered, force-include Conversion-Design as the catch-all.
6. Produce an exclusion rationale for every framework not selected.

## Output
A list of `FrameworkChoice(name, role, justification, covers)` plus an exclusion rationale list, passed to scoring and synthesis.

## Quality Gate
- Every required coverage bucket for the campaign type + jurisdiction is covered by a selected framework.
- Each inclusion has a one-sentence justification tied to the coverage it contributes.
- The selected set is the smallest that fully covers the case (no redundant frameworks).

## Reference Implementation
`src/personalized_email_campaign_designer/framework_selector.py` ? `FrameworkSelector.select()`, `FrameworkSelector.exclusion_rationale()`.
