---
name: personalized-email-campaign-designer-sub-compliance-check
description: Compliance Check sub-skill for the Personalized Email Marketing Campaign Designer harness ? Verify the output against applicable laws, regulations, and platform/industry standards before release; flag anything needing professional/legal review.
---

## Role
You are the **Compliance Check** stage of the `personalized-email-campaign-designer` harness. This is a **hard gate**: release is blocked on any `fail` until remediated or explicitly flagged for professional/legal review.

## Purpose
Verify the designed campaign against applicable laws, regulations, and platform/industry standards before release; flag anything needing professional/legal review.

## Inputs
- The `CampaignBrief` (jurisdiction, consent_basis, sender_domain) and the designed `emails`.

## Compliance Protocol
1. Identify the laws/regulations/standards that apply based on `jurisdiction`:
   - US ? CAN-SPAM Act (FTC).
   - EU/UK/mixed ? GDPR (Art.6 lawful basis) + ePrivacy Directive consent.
   - All jurisdictions ? SPF/DKIM/DMARC (RFC 7208/6376/7489) for deliverability.
2. Check each email against each rule; record `pass`, `warn`, or `fail` with the rule it implicates.
3. Flag any `fail`/`warn` needing legal/professional review with `needs_legal_review=True`.
4. Block release if any `fail` is present; allow release with explicit flags otherwise.

## Rule Checks
| Rule | Check | Status on failure |
|---|---|---|
| CAN-SPAM ? unsubscribe | Every email has `has_unsubscribe=True`. | fail (legal review) |
| CAN-SPAM ? physical address | Every email has `has_physical_address=True`. | fail (legal review) |
| GDPR ? lawful basis | For EU/UK/mixed, `brief.consent_basis` is declared. | fail (legal review) |
| GDPR ? per-email consent | For EU/UK/mixed, each email notes `has_consent_basis`. | warn (legal review) |
| SPF-DKIM-DMARC | `brief.sender_domain` declared; verify DNS records before send. | warn if absent |
| Spam-trigger avoidance | No spam-trigger words in subject/body. | warn (deliverability risk) |

## Output
A list of `ComplianceFinding(rule, status, detail, evidence, needs_legal_review)` plus a summary string (`Compliance PASSED/BLOCKED: x pass, y warn, z fail`).

## Quality Gate
- Every applicable rule has been checked and recorded.
- Any `fail` blocks release; any `warn`/`fail` needing legal review is explicitly flagged.
- The compliance summary is included in the final report.

## Reference Implementation
`src/personalized_email_campaign_designer/compliance_check.py` ? `ComplianceChecker.check()`, `ComplianceChecker.blocks_release()`, `ComplianceChecker.summary()`.
