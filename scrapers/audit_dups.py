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
    # performance-type / accessibility suffix after a dash (so an unhandled
    # "… - Relaxed Performance" gets flagged as a de-dup miss next time)
    t = re.sub(r"\s*[-–—:]\s*(?:relaxed|captioned|audio[- ]?describ\w*|signed|bsl|"
               r"matinee|opening night|press night|gala night|previews?|sensory|"
               r"autism[- ]?friendly|dementia[- ]?friendly|touch tour|sing[- ]?along|"
               r"auslan)\b.*$", "", t, flags=re.I)
    return group_key(t)


def main():
    shows = json.loads((DATA / "shows.json").read_text(encoding="utf-8"))["shows"]
    g2t = defaultdict(set)
    for s in shows:
        g2t[s["group"]].add(s["title"])

    # works_distinct.json 拆出的「同名異作」group 是刻意分裂(義原創 Peter Pan vs
    # 英美 Peter Pan,2026-07-14),不算 de-dup miss。
    wd = DATA / "works_distinct.json"
    distinct_groups = set()
    if wd.exists():
        for r in json.loads(wd.read_text(encoding="utf-8")).get("rules", []):
            if r.get("group"):
                distinct_groups.add(r["group"])

    loose2groups = defaultdict(set)
    for g, titles in g2t.items():
        if g in distinct_groups:
            continue
        loose2groups[loose_key(sorted(titles, key=len)[0])].add(g)
    misses = {lk: gs for lk, gs in loose2groups.items() if len(gs) > 1}

    promo = sorted({s["title"] for s in shows if _PROMO.search(s["title"])})
    junk = sorted({s["title"] for s in shows if _JUNK.search(s["title"])})

    # 季票假日期指紋(2026-07-14 Scranton/Little Rock/Lexington 案):同 venue+city、
    # 完全相同 start~end、≥3 個不同 group = TM season-subscription event 的起賣日被當
    # 演出日。scraper 已擋 subscription 字樣,這裡守「沒想到的變種」。
    vd = defaultdict(set)
    for s in shows:
        if s.get("venue") and s.get("start_date"):
            vd[(s["venue"], s.get("city"), s["start_date"], s.get("end_date"))].add(s["group"])
    sub_susp = {k: gs for k, gs in vd.items() if len(gs) >= 3}

    problems = 0
    if sub_susp:
        problems += len(sub_susp)
        print(f"✗ {len(sub_susp)} same-venue same-dates ≥3-show cluster(s) (season-subscription 假日期嫌疑):")
        for (v, c, st, en), gs in sorted(sub_susp.items()):
            print(f"    {v} @ {c} {st}~{en}: {sorted(gs)}")
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
