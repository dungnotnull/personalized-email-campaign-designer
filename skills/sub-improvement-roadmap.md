---
name: personalized-email-campaign-designer-sub-improvement-roadmap
description: Improvement Roadmap sub-skill for the Personalized Email Marketing Campaign Designer harness ? Generate a prioritized, effort/impact-ranked set of recommendations traceable to the scored findings.
---

## Role
You are the **Improvement Roadmap** stage of the `personalized-email-campaign-designer` harness.

## Purpose
Translate the scored findings and compliance issues into a prioritized, effort ? impact ranked set of recommendations traceable to the rubric.

## Inputs
- The `Scorecard` from `sub-scoring-engine`.
- The `ComplianceFinding` list from `sub-compliance-check`.
- The `segments` and `emails` (for copy-level fixes).

## Process
1. For every dimension scoring below 85, generate an item focused on its weakest sub-score; set effort (1-5) and impact (1-5) from the gap and fix type.
2. For every compliance `warn`/`fail`, generate a remediation item (impact 5 for fails, 3 for warns).
3. For segment gaps (missing segments, missing RFM labels, <2 personalization tokens) generate targeted items.
4. For email-level copy gaps (subject outside 28-50 chars, missing preview text, ?1 CTA) generate targeted items.
5. De-duplicate by title (keep the highest priority instance).
6. Rank by `priority = impact / effort`, descending, then by impact.
7. Bucket each item into a quadrant: **quick-win** (impact?4, effort?2), **major-project** (impact?4, effort?3), **fill-in** (impact?2, effort?2), **thankless** (rest).

## Output
A ranked list of `RoadmapItem(title, finding, effort, impact, dimension, evidence)` plus a markdown table (effort ? impact ? quadrant ? finding).

## Quality Gate
- Every item is traceable to a scored dimension or compliance finding.
- Items are ordered by impact/effort and bucketed into quadrants.
- No item is generic boilerplate; each cites the specific finding it addresses.

## Reference Implementation
`src/personalized_email_campaign_designer/improvement_roadmap.py` ? `ImprovementRoadmap.build()`, `ImprovementRoadmap.render_table()`, `RoadmapItem.priority`, `RoadmapItem.quadrant`.
