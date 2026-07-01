# -*- coding: utf-8 -*-
"""knowledge_updater.py - self-improving crawl pipeline for Skill #151
(Personalized Email Marketing Campaign Designer, cluster: marketing-content-branding).

Pattern (per CLAUDE.md):
  1. crawl4ai -> fetch latest standards/industry pages from domain sources (optional).
  2. ArXiv API (stdlib urllib) -> latest cs.IR papers relevant to email/recommendation.
  3. Parse -> title, authors, date, DOI/URL, abstract, key findings.
  4. Score -> rank by recency + domain-keyword relevance.
  5. Dedup -> skip entries already present (URL/DOI hash).
  6. Append -> add scored entries to SECOND-KNOWLEDGE-BRAIN.md (date-stamped).

Recommended schedule: weekly cron. Graceful degradation: if the network or any
optional dependency is unavailable, the tool logs and exits 0 so the skill keeps
working off the existing knowledge base.

Usage:
    python tools/knowledge_updater.py                 # live crawl + append
    python tools/knowledge_updater.py --dry-run       # show what would be appended
    python tools/knowledge_updater.py --max 5         # cap entries per run
    python tools/knowledge_updater.py --brain PATH     # override brain path
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import Dict, List, Optional

# Make the package importable when run as a standalone script.
_HERE = os.path.dirname(os.path.abspath(__file__))
_SRC = os.path.abspath(os.path.join(_HERE, "..", "src"))
if _SRC not in sys.path and os.path.isdir(_SRC):
    sys.path.insert(0, _SRC)

from personalized_email_campaign_designer.knowledge_brain import KnowledgeBrain  # noqa: E402

ARXIV_CATEGORIES = ["cs.IR"]
ARXIV_API = "http://export.arxiv.org/api/query"
ARXIV_QUERY = (
    '(abs:"email" OR abs:"personalization" OR abs:"recommendation" OR abs:"conversion")'
)
WEB_SOURCES = [
    "https://www.litmus.com",
    "https://mailchimp.com/resources",
    "https://www.campaignmonitor.com",
    "https://gdpr.eu",
]
SEARCH_QUERIES = [
    "email marketing benchmarks open rate 2026",
    "email deliverability DMARC best practice",
    "persuasion copywriting email conversion",
    "GDPR CAN-SPAM email compliance",
]
USER_AGENT = "skill151-knowledge-updater/1.0 (+https://github.com/skills/personalized-email-campaign-designer)"

# Atom namespace used by the ArXiv API.
_ATOM = "{http://www.w3.org/2005/Atom}"
_ARXIV = "{http://arxiv.org/schemas/atom}"


@dataclass
class Entry:
    title: str
    authors: List[str] = field(default_factory=list)
    year: str = ""
    venue: str = ""
    url: str = ""
    abstract: str = ""
    kind: str = "paper"

    @property
    def hash(self) -> str:
        return KnowledgeBrain.url_hash(self.url)


def relevance_score(title: str, abstract: str) -> float:
    """Fraction of domain keywords present in title+abstract."""
    blob = (title + " " + abstract).lower()
    keywords = sorted({w for q in SEARCH_QUERIES for w in q.split()})
    hits = sum(1 for k in keywords if k in blob)
    return round(hits / max(1, len(keywords)), 3)


def _fetch(url: str, timeout: int = 20) -> Optional[str]:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "*/*"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        print(f"[warn] fetch failed {url}: {e}")
        return None


def fetch_arxiv(max_results: int = 25) -> List[Entry]:
    """Query the ArXiv export API over stdlib urllib; degrade gracefully."""
    query = urllib.parse.urlencode({
        "search_query": f"cat:cs.IR AND {ARXIV_QUERY}",
        "start": 0,
        "max_results": max_results,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    })
    url = f"{ARXIV_API}?{query}"
    xml = _fetch(url)
    if not xml:
        return []
    return _parse_arxiv(xml)


def _parse_arxiv(xml: str) -> List[Entry]:
    entries: List[Entry] = []
    try:
        root = ET.fromstring(xml)
    except ET.ParseError as e:
        print(f"[warn] arxiv xml parse failed: {e}")
        return entries
    for el in root.findall(f"{_ATOM}entry"):
        title = (el.findtext(f"{_ATOM}title") or "").strip().replace("\n", " ")
        url = (el.findtext(f"{_ATOM}id") or "").strip()
        abstract = (el.findtext(f"{_ATOM}summary") or "").strip().replace("\n", " ")
        published = (el.findtext(f"{_ATOM}published") or "")[:4]
        authors = [(a.findtext(f"{_ATOM}name") or "") for a in el.findall(f"{_ATOM}author")]
        venue = "arXiv"
        if title and url:
            entries.append(Entry(title=title, authors=authors, year=published,
                                 venue=venue, url=url, abstract=abstract, kind="paper"))
    return entries


def fetch_web_sources() -> List[Entry]:
    """Fetch authoritative web sources; uses crawl4ai when available, else urllib."""
    entries: List[Entry] = []
    try:
        from crawl4ai import WebCrawler  # type: ignore
    except Exception:
        crawl4ai = None
    else:
        crawl4ai = "available"
        crawler = WebCrawler()
        try:
            crawler.warmup()
        except Exception as e:
            print(f"[warn] crawl4ai warmup failed: {e}")
            crawl4ai = None
    for src in WEB_SOURCES:
        md = ""
        if crawl4ai:
            try:
                res = crawler.run(url=src)
                md = getattr(res, "markdown", "") or ""
            except Exception as e:
                print(f"[warn] crawl4ai source {src}: {e}")
        if not md:
            md = _fetch(src) or ""
        if not md.strip():
            continue
        snippet = re.sub(r"\s+", " ", md)[:500]
        entries.append(Entry(
            title=f"Domain update scan: {src}",
            authors=["-"], year=str(datetime.date.today().year),
            venue=src, url=src, abstract=snippet, kind="web",
        ))
    return entries


def fetch_entries(max_results: int = 25) -> List[Entry]:
    """Collect entries from all sources; degrade gracefully per-source."""
    entries: List[Entry] = []
    try:
        entries.extend(fetch_arxiv(max_results=max_results))
    except Exception as e:
        print(f"[warn] arxiv fetch error: {e}")
    try:
        entries.extend(fetch_web_sources())
    except Exception as e:
        print(f"[warn] web fetch error: {e}")
    return entries


def render_entry(entry: Entry, today: str) -> str:
    rel = relevance_score(entry.title, entry.abstract)
    authors = ", ".join(entry.authors[:3]) + (" et al." if len(entry.authors) > 3 else "")
    finding = entry.abstract[:200].strip() or "-"
    return (
        f"- {today} -- **{entry.title}** ({authors}, {entry.venue}, {entry.year or '-'}) "
        f"[{entry.url}] relevance={rel:.2f} | finding: {finding} <!--hash:{entry.hash}-->"
    )


def append_entries(entries: List[Entry], brain_path: Optional[str] = None,
                    max_entries: int = 50, dry_run: bool = False) -> int:
    brain = KnowledgeBrain(brain_path)
    if not brain.exists():
        print(f"[error] knowledge brain not found: {brain.path}")
        return 0
    seen = brain.hashes()
    scored = sorted(entries, key=lambda e: relevance_score(e.title, e.abstract), reverse=True)
    today = datetime.date.today().isoformat()
    lines: List[str] = []
    for e in scored:
        if len(lines) >= max_entries:
            break
        if not e.url or e.hash in seen:
            continue
        if relevance_score(e.title, e.abstract) <= 0:
            continue
        lines.append(render_entry(e, today))
        seen.add(e.hash)
    if not lines:
        print("[info] no new entries this run (network/dedup/relevance).")
        return 0
    if dry_run:
        print(f"[dry-run] would append {len(lines)} entries:")
        for line in lines:
            print(line)
        return len(lines)
    added = brain.append_section(f"Auto-crawl {today}", lines, dedup=True)
    print(f"[ok] appended {added} new entries to {brain.path}")
    return added


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Grow SECOND-KNOWLEDGE-BRAIN.md for Skill #151.")
    parser.add_argument("--dry-run", action="store_true", help="Show entries without writing.")
    parser.add_argument("--max", type=int, default=50, help="Max entries to append per run.")
    parser.add_argument("--arxiv-max", type=int, default=25, help="Max ArXiv results to fetch.")
    parser.add_argument("--brain", help="Override SECOND-KNOWLEDGE-BRAIN.md path.")
    parser.add_argument("--no-web", action="store_true", help="Skip web source crawl.")
    args = parser.parse_args(argv)

    print(f"[run] knowledge_updater for skill #151 (personalized-email-campaign-designer)")
    entries = fetch_arxiv(max_results=args.arxiv_max)
    if not args.no_web:
        entries += fetch_web_sources()
    n = append_entries(entries, brain_path=args.brain, max_entries=args.max, dry_run=args.dry_run)
    print(f"[done] processed {len(entries)} candidate(s); {'dry-run ' if args.dry_run else ''}{n} new.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
