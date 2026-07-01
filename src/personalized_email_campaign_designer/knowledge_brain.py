# -*- coding: utf-8 -*-
"""Reader / writer for ``SECOND-KNOWLEDGE-BRAIN.md`` (self-improving knowledge base).

Provides keyword search over the brain and a deduplicated append path used by
``tools/knowledge_updater.py``. Pure standard library so it works offline.
"""
from __future__ import annotations

import hashlib
import os
import re
from dataclasses import dataclass
from typing import List, Optional

DEFAULT_BRAIN = os.path.join(os.path.dirname(__file__), "..", "..", "SECOND-KNOWLEDGE-BRAIN.md")

_HASH_RE = re.compile(r"<!--hash:([0-9a-f]{16})-->")


@dataclass
class BrainEntry:
    line: str
    hash: Optional[str] = None


class KnowledgeBrain:
    def __init__(self, path: Optional[str] = None):
        self.path = os.path.abspath(path or DEFAULT_BRAIN)

    def exists(self) -> bool:
        return os.path.exists(self.path)

    def read(self) -> str:
        if not self.exists():
            return ""
        with open(self.path, "r", encoding="utf-8") as f:
            return f.read()

    def hashes(self) -> set:
        return set(_HASH_RE.findall(self.read()))

    def search(self, query: str, limit: int = 20) -> List[str]:
        """Return matching lines (case-insensitive, all query terms OR'd)."""
        terms = [t.lower() for t in query.split() if t]
        matches = []
        for line in self.read().splitlines():
            low = line.lower()
            if any(t in low for t in terms):
                matches.append(line)
            if len(matches) >= limit:
                break
        return matches

    def append_section(self, header: str, lines: List[str], dedup: bool = True) -> int:
        """Append a dated section; returns number of new lines actually added."""
        seen = self.hashes() if dedup else set()
        added: List[str] = []
        for line in lines:
            m = _HASH_RE.search(line)
            h = m.group(1) if m else None
            if h and h in seen:
                continue
            if h:
                seen.add(h)
            added.append(line)
        if not added:
            return 0
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(f"\n### {header}\n" + "\n".join(added) + "\n")
        return len(added)

    @staticmethod
    def url_hash(url: str) -> str:
        return hashlib.sha256((url or "").encode("utf-8")).hexdigest()[:16]
