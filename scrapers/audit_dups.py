"""Self-check for de-dup misses + leftover junk in data/shows.json.

Run after every build so grouping problems surface HERE, not from a user spotting
two cards for the same show. Flags:
  1. de-dup misses — distinct groups that collapse under a looser key (strip a
     trailing parenthetical / promoter prefix / punctuation → same canonical group).
  2. promoter-prefix residue ("… presents …", "… production of …").
  3. upsell junk that slipped through ("… packages", "ticket+ hotel", VIP, …).

Exit code 1 if anything is flagged (so CI / a pre-commit check can catch it).
Run: python scrapers/audit_dups.py
"""

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

from build_shows import group_key   # same normalisation the build uses

DATA = Path(__file__).resolve().parent.parent / "data"

_PROMO = re.compile(r"\b(?:presents|production of)\b", re.I)
_JUNK = re.compile(r"\bpackages?\b|ticket\s*\+|\bvip\b|meet (?:and|&) greet", re.I)


def loose_key(title):
    t = re.sub(r"^.{0,70}?\b(?:presents|production of)\b\s*:?\s+", "", title, flags=re.I)
    t = re.sub(r"\s*\([^)]*\)\s*$", "", t)          # trailing parenthetical
    return group_key(t)


def main():
    shows = json.loads((DATA / "shows.json").read_text(encoding="utf-8"))["shows"]
    g2t = defaultdict(set)
    for s in shows:
        g2t[s["group"]].add(s["title"])

    loose2groups = defaultdict(set)
    for g, titles in g2t.items():
        loose2groups[loose_key(sorted(titles, key=len)[0])].add(g)
    misses = {lk: gs for lk, gs in loose2groups.items() if len(gs) > 1}

    promo = sorted({s["title"] for s in shows if _PROMO.search(s["title"])})
    junk = sorted({s["title"] for s in shows if _JUNK.search(s["title"])})

    problems = 0
    if misses:
        problems += len(misses)
        print(f"✗ {len(misses)} de-dup MISS (same show, split groups):")
        for lk, gs in sorted(misses.items()):
            print(f"    [{lk}]")
            for g in sorted(gs):
                print(f"        {g!r}: {sorted(g2t[g])}")
    if promo:
        problems += len(promo)
        print(f"✗ {len(promo)} promoter-prefix residue: {promo}")
    if junk:
        problems += len(junk)
        print(f"✗ {len(junk)} upsell-junk residue: {junk}")

    if problems:
        print(f"\nAUDIT FAILED: {problems} issue(s) — fix in build_shows.py before commit.")
        sys.exit(1)
    print(f"AUDIT OK: {len(shows)} shows, {len(g2t)} groups, 0 de-dup misses / promoter / junk.")


if __name__ == "__main__":
    main()
