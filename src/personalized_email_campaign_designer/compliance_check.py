# -*- coding: utf-8 -*-
"""``sub-compliance-check`` - Compliance Check.

Verifies a designed campaign against applicable laws / regulations / platform
standards and blocks release until issues are resolved or explicitly flagged for
professional/legal review. The checks are deterministic and offline-safe; they
examine the email drafts plus the sender-domain posture declared in the brief.
"""
from __future__ import annotations

from typing import List

from .schemas import CampaignBrief, ComplianceFinding, EmailMessage, Evidence, Certainty
from .scoring_engine import SPAM_TRIGGERS


class ComplianceChecker:
    """Rule-based compliance audit (CAN-SPAM, GDPR/ePrivacy, deliverability)."""

    def check(self, brief: CampaignBrief, emails: List[EmailMessage]) -> List[ComplianceFinding]:
        findings: List[ComplianceFinding] = []
        findings.extend(self._can_spam(emails))
        findings.extend(self._gdpr(brief, emails))
        findings.extend(self._deliverability(brief, emails))
        findings.extend(self._spam_triggers(emails))
        return findings

    def blocks_release(self, findings: List[ComplianceFinding]) -> bool:
        return any(f.status == "fail" for f in findings)

    def summary(self, findings: List[ComplianceFinding]) -> str:
        fails = sum(1 for f in findings if f.status == "fail")
        warns = sum(1 for f in findings if f.status == "warn")
        passes = sum(1 for f in findings if f.status == "pass")
        verdict = "BLOCKED" if fails else "PASSED"
        return f"Compliance {verdict}: {passes} pass, {warns} warn, {fails} fail."

    def _can_spam(self, emails: List[EmailMessage]) -> List[ComplianceFinding]:
        out: List[ComplianceFinding] = []
        rule = "CAN-SPAM"
        ev = Evidence("CAN-SPAM Act 2008: unsubscribe + physical postal address required.",
                      url="https://www.ftc.gov/legal-library/browse/rules/can-spam-act",
                      framework="CAN-SPAM", certainty=Certainty.HIGH)
        for e in emails:
            if not e.has_unsubscribe:
                out.append(ComplianceFinding(rule=rule, status="fail",
                            detail=f"Email '{e.name}' has no unsubscribe mechanism.",
                            evidence=ev, needs_legal_review=True))
            if not e.has_physical_address:
                out.append(ComplianceFinding(rule=rule, status="fail",
                            detail=f"Email '{e.name}' has no physical postal address.",
                            evidence=ev, needs_legal_review=True))
        if emails and all(e.has_unsubscribe and e.has_physical_address for e in emails):
            out.append(ComplianceFinding(rule=rule, status="pass",
                        detail="All emails include a working unsubscribe and physical address.", evidence=ev))
        return out

    def _gdpr(self, brief: CampaignBrief, emails: List[EmailMessage]) -> List[ComplianceFinding]:
        out: List[ComplianceFinding] = []
        if brief.jurisdiction not in {"EU", "UK", "mixed"}:
            return out
        rule = "GDPR/ePrivacy"
        ev = Evidence("GDPR Art.6 lawful basis + ePrivacy consent for electronic marketing.",
                      url="https://gdpr.eu/article-6-how-to-process-personal-data-legally/",
                      framework="GDPR", certainty=Certainty.HIGH)
        if not brief.consent_basis:
            out.append(ComplianceFinding(rule=rule, status="fail",
                        detail="No GDPR lawful basis declared for EU/UK recipients.",
                        evidence=ev, needs_legal_review=True))
        else:
            out.append(ComplianceFinding(rule=rule, status="pass",
                        detail=f"Lawful basis declared: {brief.consent_basis}.", evidence=ev))
        missing = [e.name for e in emails if not e.has_consent_basis]
        if missing:
            out.append(ComplianceFinding(rule=rule, status="warn",
                        detail=f"Emails without consent-basis note: {', '.join(missing)}.",
                        evidence=ev, needs_legal_review=True))
        return out

    def _deliverability(self, brief: CampaignBrief, emails: List[EmailMessage]) -> List[ComplianceFinding]:
        out: List[ComplianceFinding] = []
        rule = "SPF-DKIM-DMARC"
        ev = Evidence("RFC 7208 (SPF), RFC 6376 (DKIM), RFC 7489 (DMARC) for sender authentication.",
                      framework="SPF-DKIM-DMARC", certainty=Certainty.HIGH)
        if not brief.sender_domain:
            out.append(ComplianceFinding(rule=rule, status="warn",
                        detail="No sending domain declared; SPF/DKIM/DMARC posture cannot be verified.",
                        evidence=ev))
        else:
            out.append(ComplianceFinding(rule=rule, status="pass",
                        detail=f"Sending domain '{brief.sender_domain}' declared; verify SPF/DKIM/DMARC records in DNS before send.",
                        evidence=ev))
        return out

    def _spam_triggers(self, emails: List[EmailMessage]) -> List[ComplianceFinding]:
        out: List[ComplianceFinding] = []
        rule = "spam-trigger avoidance"
        ev = Evidence("Mailchimp/Return Path: spam-trigger words harm inbox placement.",
                      framework="CAN-SPAM", certainty=Certainty.MEDIUM)
        hits = {}
        for e in emails:
            blob = ((e.subject_line or "") + " " + (e.body or "")).lower()
            found = sorted({w for w in SPAM_TRIGGERS if w in blob})
            if found:
                hits[e.name] = found
        if hits:
            detail = "; ".join(f"{n}: {', '.join(ws)}" for n, ws in hits.items())
            out.append(ComplianceFinding(rule=rule, status="warn",
                        detail=f"Spam-trigger words detected -> {detail}.", evidence=ev))
        else:
            out.append(ComplianceFinding(rule=rule, status="pass",
                        detail="No spam-trigger words detected in subject or body.", evidence=ev))
        return out
