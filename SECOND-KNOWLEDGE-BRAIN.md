# SECOND-KNOWLEDGE-BRAIN.md ? Personalized Email Marketing Campaign Designer (Skill #151)

> Self-improving domain knowledge base. Grown by `tools/knowledge_updater.py` (weekly cron). Newest evidence is preferred per the evidence hierarchy (Systematic Review > Meta-Analysis > RCT > Cohort > Expert Opinion > Blog).

## Core Concepts & Frameworks
- **AIDA & PAS copy frameworks** ? Structure subject, body, and CTA persuasion (Attention-Interest-Desire-Action; Problem-Agitate-Solve).
- **Cialdini's principles of influence** ? Reciprocity, commitment, social proof, authority, liking, scarcity.
- **RFM segmentation** ? Recency-Frequency-Monetary audience targeting.
- **Deliverability standards (SPF/DKIM/DMARC)** ? Inbox placement and sender reputation (RFC 7208/6376/7489).
- **CAN-SPAM & GDPR consent rules** ? Legal compliance for commercial email (US CAN-SPAM Act; EU GDPR + ePrivacy).

## Key Research Papers & Standards (curated seed)
| Title | Authors | Year | Venue | DOI/Link | Relevance |
|---|---|---|---|---|---|
| Influence: The Psychology of Persuasion | Cialdini, R. B. | 1984/2021 | Book (Harper Business) | https://www.influenceatwork.com | Cialdini's six principles ? the persuasion backbone of copy scoring. |
| The Complete Database Marketer (RFM) | Hughes, A. M. | 1996 | Book (McGraw-Hill) | ? | Foundational Recency-Frequency-Monetary segmentation. |
| RFC 7208 ? Sender Policy Framework (SPF) | Kitterman, S. | 2014 | IETF RFC | https://www.rfc-editor.org/rfc/rfc7208 | SPF authentication standard for deliverability. |
| RFC 6376 ? DomainKeys Identified Mail (DKIM) | Crocker et al. | 2011 | IETF RFC | https://www.rfc-editor.org/rfc/rfc6376 | DKIM signing standard. |
| RFC 7489 ? Domain-based Message Authentication (DMARC) | Kucherawy, Lindsey | 2015 | IETF RFC | https://www.rfc-editor.org/rfc/rfc7489 | DMARC policy alignment for inbox placement. |
| CAN-SPAM Act: A Compliance Guide for Business | FTC | 2009 (updated) | US FTC guidance | https://www.ftc.gov/legal-library/browse/rules/can-spam-act | US legal baseline (unsubscribe, physical address). |
| GDPR ? Article 6 Lawful Basis | EU | 2016 | Regulation (EU) 2016/679 | https://gdpr.eu/article-6-how-to-process-personal-data-legally | EU lawful basis for electronic marketing. |
| Email Client Market Share / Subject-line benchmarks | Litmus | ongoing | Industry benchmark | https://www.litmus.com | Open-rate and rendering benchmarks (28-50 char subject ideal). |
| Email Marketing Benchmarks | Mailchimp | ongoing | Industry benchmark | https://mailchimp.com/resources | Open/CTR benchmarks and spam-trigger guidance. |
| ePrivacy Directive 2002/58/EC | EU | 2002 (amended 2009) | EU Directive | https://eur-lex.europa.eu | Consent rules for electronic marketing in the EU. |

> The first live crawl (`tools/knowledge_updater.py`) will append dated, deduplicated ArXiv + web entries below as `### Auto-crawl YYYY-MM-DD` sections. Do not edit curated rows above without a source citation.

## State-of-the-Art Methods & Tools
- Apply the frameworks above as the scoring backbone.
- Prefer primary standards documents (RFCs, statutes) and peer-reviewed sources over secondary blogs.
- Combine quantitative scoring with a qualitative challenge stage.
- Authenticate senders with SPF + DKIM + DMARC alignment; monitor sender reputation and complaint rate.

## Authoritative Data Sources
- https://www.litmus.com
- https://mailchimp.com/resources
- https://www.campaignmonitor.com
- https://gdpr.eu
- ArXiv: cs.IR

## Analytical Frameworks (Scoring Backbone)
| Framework / Standard | Role in this skill |
|---|---|
| AIDA & PAS copy frameworks | Structure subject, body, and CTA persuasion. |
| Cialdini's principles of influence | Reciprocity, scarcity, social proof in copy. |
| RFM segmentation | Recency-Frequency-Monetary audience targeting. |
| Deliverability standards (SPF/DKIM/DMARC) | Inbox placement and sender reputation. |
| CAN-SPAM & GDPR consent rules | Legal compliance for commercial email. |

## Self-Update Protocol (crawl4ai config)
- **Sources:** the authoritative URLs above + ArXiv categories (cs.IR).
- **Search queries:**
  - `email marketing benchmarks open rate`
  - `email deliverability DMARC best practice`
  - `persuasion copywriting email conversion`
  - `GDPR CAN-SPAM email compliance`
- **Frequency:** weekly.
- **Append format:** dated section (`### Auto-crawl YYYY-MM-DD`) with Title, Authors, Year, Venue, DOI/URL, key finding, relevance note, and a `<!--hash:...-->` dedup marker.
- **Dedup:** skip entries whose URL/DOI hash already exists in the brain.

## Knowledge Update Log
- 2026-06-18 ? Knowledge base seeded at skill creation (frameworks + sources).
- 2026-07-01 ? Brain re-seeded with citable, real-world frameworks/standards (Cialdini, Hughes RFM, RFC 7208/6376/7489, CAN-SPAM, GDPR/ePrivacy, Litmus/Mailchimp benchmarks). First live ArXiv crawl deferred to production stage (run `python tools/knowledge_updater.py`).
