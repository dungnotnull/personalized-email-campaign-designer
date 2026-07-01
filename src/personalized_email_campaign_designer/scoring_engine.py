# -*- coding: utf-8 -*-
"""``sub-scoring-engine`` - Scoring Engine.

Applies the multi-dimensional rubric to produce 0-100 scores with cited evidence
per dimension and computes the weighted total mapped to a letter grade. The
heuristics are deterministic and offline-safe; each sub-score is computed from
observable features of the designed emails / segments so the result is
reproducible and auditable.
"""
from __future__ import annotations

from typing import Dict, List

from .schemas import (
    CampaignBrief,
    DimensionScore,
    EmailMessage,
    Evidence,
    Scorecard,
    Segment,
    Certainty,
)

# Canonical rubric (must sum to 1.0).
DIMENSIONS = [
    ("Subject & preview (open rate)", 0.25),
    ("Segmentation & personalization", 0.25),
    ("Persuasion & copy quality", 0.20),
    ("Deliverability & compliance", 0.20),
    ("Conversion design (CTA/flow)", 0.10),
]


def letter_grade(overall: float) -> str:
    if overall >= 90:
        return "A"
    if overall >= 75:
        return "B"
    if overall >= 60:
        return "C"
    return "D"


# Spam-trigger lexicon (lowercase). Source: common Mailchimp/Return Path guidance.
SPAM_TRIGGERS = {
    "free", "guarantee", "winner", "act now", "limited time", "buy now", "click here",
    "urgent", "money", "credit", "loan", "viagra", "casino", "lottery", "congratulations",
    "100% free", "risk-free", "no obligation", "earn money", "work from home",
    "weight loss", "cialis", "dear friend", "this is not spam", "order now",
}

# Power / curiosity words that lift open rates when used sparingly.
POWER_WORDS = {
    "you", "your", "new", "now", "today", "introducing", "finally", "secret",
    "tips", "guide", "how to", "why", "what", "save", "inside", "update", "ready",
}

PREVIEW_BEST_LEN = (35, 90)
SUBJECT_BEST_LEN = (28, 50)


def _contains_any(haystack: str, words) -> int:
    h = haystack.lower()
    return sum(1 for w in words if w in h)


class ScoringEngine:
    """Score a designed campaign against the rubric."""

    def score(self, brief: CampaignBrief, segments: List[Segment], emails: List[EmailMessage], degraded: bool = False) -> Scorecard:
        if not emails:
            emails = [EmailMessage(position=1, name="draft", segment="all", subject_line="", body="")]
        certainty = Certainty.STALE if degraded else Certainty.HIGH
        dims: List[DimensionScore] = []
        for name, weight in DIMENSIONS:
            fn = {
                "Subject & preview (open rate)": self._score_subject,
                "Segmentation & personalization": self._score_segmentation,
                "Persuasion & copy quality": self._score_persuasion,
                "Deliverability & compliance": self._score_deliverability,
                "Conversion design (CTA/flow)": self._score_conversion,
            }[name]
            sub_scores, rationale, evidence = fn(brief, segments, emails, certainty)
            raw = sum(sub_scores.values()) / max(1, len(sub_scores))
            score = int(round(max(0, min(100, raw))))
            dims.append(
                DimensionScore(
                    dimension=name,
                    weight=weight,
                    score=score,
                    rationale=rationale,
                    evidence=evidence,
                    sub_scores=sub_scores,
                )
            )
        overall = sum(d.score * d.weight for d in dims)
        return Scorecard(dimensions=dims, overall=round(overall, 1), grade=letter_grade(overall))

    # ---- dimension scorers ------------------------------------------------

    def _score_subject(self, brief, segments, emails, certainty):
        sub: Dict[str, int] = {}
        length_scores, token_scores, curiosity_scores, trigger_scores, preview_scores = [], [], [], [], []
        for e in emails:
            sl = e.subject_line or ""
            length_scores.append(self._subject_length_score(sl))
            seg_tokens = segments_personalization(segments, e.segment) if e.segment else []
            has_token = any("{{" in sl or (tok and tok.lower() in sl.lower()) for tok in seg_tokens)
            token_scores.append(100 if has_token else (60 if "{{" in sl else 30))
            curiosity_scores.append(min(100, 40 + 15 * _contains_any(sl, POWER_WORDS)))
            triggers = _contains_any(sl, SPAM_TRIGGERS)
            trigger_scores.append(max(0, 100 - 25 * triggers))
            pv = e.preview_text or ""
            pl = len(pv)
            preview_scores.append(100 if PREVIEW_BEST_LEN[0] <= pl <= PREVIEW_BEST_LEN[1] else (70 if pl else 20))
        sub["length_in_ideal_range"] = avg(length_scores)
        sub["personalization_tokens"] = avg(token_scores)
        sub["curiosity_power_words"] = avg(curiosity_scores)
        sub["spam_trigger_penalty"] = avg(trigger_scores)
        sub["preview_text_present"] = avg(preview_scores)
        rationale = (
            f"Subjects averaged {avg(length_scores):.0f}/100 on length fit ({SUBJECT_BEST_LEN[0]}-{SUBJECT_BEST_LEN[1]} chars ideal), "
            f"{avg(trigger_scores):.0f}/100 on spam-trigger avoidance and {avg(preview_scores):.0f}/100 on preview text."
        )
        evidence = [
            Evidence("Litmus subject-line benchmarks (28-50 chars optimise open rate).", framework="AIDA", certainty=certainty),
            Evidence("Mailchimp: avoid spam-trigger words in subject lines.", framework="CAN-SPAM", certainty=certainty),
        ]
        return sub, rationale, evidence

    def _score_segmentation(self, brief, segments, emails, certainty):
        sub: Dict[str, int] = {}
        seg_count = len(segments)
        sub["segments_defined"] = 100 if seg_count >= 2 else (60 if seg_count == 1 else 20)
        rfm = sum(1 for s in segments if s.rfm_label)
        sub["rfm_labels_present"] = 100 if seg_count and rfm == seg_count else (50 if rfm else 10)
        tokens = sum(len(s.personalization_tokens) for s in segments)
        sub["personalization_tokens_per_segment"] = min(100, 25 * tokens) if seg_count else 10
        segment_used = sum(1 for e in emails if e.segment and any(s.name == e.segment for s in segments))
        sub["emails_target_a_segment"] = 100 if emails and segment_used == len(emails) else (60 if segment_used else 20)
        rationale = (
            f"{seg_count} segment(s) defined, {rfm} with RFM labels, {tokens} personalization token(s) total, "
            f"{segment_used}/{len(emails)} emails target a named segment."
        )
        evidence = [
            Evidence("RFM (Recency-Frequency-Monetary) segmentation improves targeting precision.", framework="RFM", certainty=certainty),
            Evidence("Behavioural personalization raises open and click rates (Campaign Monitor).", framework="RFM", certainty=certainty),
        ]
        return sub, rationale, evidence

    def _score_persuasion(self, brief, segments, emails, certainty):
        sub: Dict[str, int] = {}
        aida_scores, pas_scores, cialdini_scores, cta_scores, value_scores = [], [], [], [], []
        for e in emails:
            body = (e.body or "").lower()
            aida_scores.append(self._aida_score(body))
            pas_scores.append(self._pas_score(body))
            cialdini_scores.append(self._cialdini_score(body))
            cta_scores.append(100 if e.cta_count == 1 else (60 if e.cta_count == 2 else 30))
            value_scores.append(100 if any(w in body for w in ("value", "benefit", "save", "results", "faster")) else 50)
        sub["aida_structure"] = avg(aida_scores)
        sub["pas_structure"] = avg(pas_scores)
        sub["cialdini_levers"] = avg(cialdini_scores)
        sub["single_clear_cta"] = avg(cta_scores)
        sub["value_language"] = avg(value_scores)
        rationale = (
            f"AIDA markers {avg(aida_scores):.0f}/100, PAS {avg(pas_scores):.0f}/100, "
            f"Cialdini levers {avg(cialdini_scores):.0f}/100, single-CTA discipline {avg(cta_scores):.0f}/100."
        )
        evidence = [
            Evidence("AIDA (Attention-Interest-Desire-Action) structures persuasive email copy.", framework="AIDA", certainty=certainty),
            Evidence("Cialdini's six principles of influence raise conversion (social proof, scarcity, reciprocity).", framework="Cialdini", certainty=certainty),
            Evidence("A single clear CTA outperforms multiple competing CTAs (Mailchimp).", framework="AIDA", certainty=certainty),
        ]
        return sub, rationale, evidence

    def _score_deliverability(self, brief, segments, emails, certainty):
        sub: Dict[str, int] = {}
        unsub = sum(1 for e in emails if e.has_unsubscribe)
        sub["unsubscribe_present"] = 100 if emails and unsub == len(emails) else (50 if unsub else 0)
        addr = sum(1 for e in emails if e.has_physical_address)
        sub["physical_address_present"] = 100 if emails and addr == len(emails) else (50 if addr else 0)
        consent = sum(1 for e in emails if e.has_consent_basis)
        sub["consent_basis_present"] = 100 if emails and consent == len(emails) else (50 if consent else 0)
        body_triggers = sum(_contains_any((e.body or "") + " " + (e.subject_line or ""), SPAM_TRIGGERS) for e in emails)
        sub["spam_trigger_avoidance"] = max(0, 100 - 15 * body_triggers)
        auth = 100 if brief.sender_domain else 40
        sub["sender_authentication"] = auth
        rationale = (
            f"unsubscribe {sub['unsubscribe_present']}/100, physical address {sub['physical_address_present']}/100, "
            f"consent {sub['consent_basis_present']}/100, auth posture {auth}/100, "
            f"spam-trigger avoidance {sub['spam_trigger_avoidance']}/100."
        )
        evidence = [
            Evidence("SPF + DKIM + DMARC alignment is required for inbox placement.", framework="SPF-DKIM-DMARC", certainty=certainty),
            Evidence("CAN-SPAM requires a working unsubscribe and physical postal address.", framework="CAN-SPAM", certainty=certainty),
            Evidence("GDPR requires a documented lawful basis for EU/UK recipients.", framework="GDPR", certainty=certainty),
        ]
        return sub, rationale, evidence

    def _score_conversion(self, brief, segments, emails, certainty):
        sub: Dict[str, int] = {}
        primary = sum(1 for e in emails if e.cta_primary)
        sub["primary_cta_present"] = 100 if emails and primary == len(emails) else (50 if primary else 0)
        mobile = sum(1 for e in emails if e.subject_length <= 50 and e.preview_text)
        sub["mobile_rendering_fit"] = 100 if emails and mobile == len(emails) else (60 if mobile else 20)
        alignment = sum(1 for e in emails if e.cta_primary and e.cta_primary.lower() in (e.body or "").lower())
        sub["cta_landing_alignment"] = 100 if emails and alignment == len(emails) else (50 if alignment else 10)
        rationale = (
            f"primary CTA {sub['primary_cta_present']}/100, mobile fit {sub['mobile_rendering_fit']}/100, "
            f"CTA-landing alignment {sub['cta_landing_alignment']}/100."
        )
        evidence = [
            Evidence("Above-the-fold CTA and mobile-first preview lift conversion (Litmus).", framework="Conversion-Design", certainty=certainty),
            Evidence("CTA copy must match the landing-page promise to reduce friction.", framework="Conversion-Design", certainty=certainty),
        ]
        return sub, rationale, evidence

    # ---- helpers ----------------------------------------------------------

    @staticmethod
    def _subject_length_score(sl: str) -> int:
        n = len(sl)
        if not sl:
            return 10
        lo, hi = SUBJECT_BEST_LEN
        if lo <= n <= hi:
            return 100
        # decay outside the ideal band
        dist = min(abs(n - lo), abs(n - hi))
        return max(30, 100 - 3 * dist)

    @staticmethod
    def _aida_score(body: str) -> int:
        markers = 0
        if any(w in body for w in ("introducing", "new", "announcing")):
            markers += 1  # Attention
        if any(w in body for w in ("because", "here is why", "learn", "discover")):
            markers += 1  # Interest
        if any(w in body for w in ("you will", "benefit", "results", "value")):
            markers += 1  # Desire
        if any(w in body for w in ("click", "get started", "claim", "join", "sign up", "start")):
            markers += 1  # Action
        return 25 * markers

    @staticmethod
    def _pas_score(body: str) -> int:
        markers = 0
        if any(w in body for w in ("problem", "struggle", "stuck", "frustrated")):
            markers += 1  # Problem
        if any(w in body for w in ("worse", "costs you", "risk", "missing out")):
            markers += 1  # Agitate
        if any(w in body for w in ("here is the fix", "solution", "we built", "try", "get")):
            markers += 1  # Solve
        return int(100 * markers / 3)

    @staticmethod
    def _cialdini_score(body: str) -> int:
        levers = 0
        if any(w in body for w in ("free", "gift", "included")):
            levers += 1  # reciprocity
        if any(w in body for w in ("join", "thousands", "customers", "loved by")):
            levers += 1  # social proof
        if any(w in body for w in ("limited", "only", "expires", "today", "last")):
            levers += 1  # scarcity
        if any(w in body for w in ("expert", "certified", "trusted", "recommended")):
            levers += 1  # authority
        if any(w in body for w in ("we", "our team", "personally")):
            levers += 1  # liking
        if any(w in body for w in ("start your", "confirm", "you are in")):
            levers += 1  # commitment
        return min(100, 16 * levers)


def segments_personalization(segments: List[Segment], name: str):
    for s in segments:
        if s.name == name:
            return s.personalization_tokens
    return []


def avg(values) -> float:
    values = list(values)
    return sum(values) / len(values) if values else 0.0
