# -*- coding: utf-8 -*-
"""Catalog hygiene auditor — scans data/shows.json for the dirty-title/data
classes we've been bitten by. Run manually after big scrapes or on demand:

    python scrapers/audit_catalog.py

Read-only: prints a categorized suspect list; fixes go through clean_title
rules / overrides.json / not_musical.json as appropriate. Categories:
  A dash/colon marketing-or-notice tails   B quoted-title marketing pattern
  C likely non-musical (movie/tribute/…)   D package/experience listings
  E presenter prefixes                     F over-long titles (>62)
  G ALL-CAPS Latin titles                  H tour_name not containing title
  I no dates at all                        J no coordinates (invisible on map)
  K near-duplicate groups at same venue+city
每類都要人工判讀 — 會有假警報(真劇名帶 Burlesque/城市/副標),別盲修。
"""
import json, re, sys, io, collections
from pathlib import Path
from difflib import SequenceMatcher

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
DATA = Path(__file__).resolve().parent.parent / "data"

d = json.loads((DATA / "shows.json").read_text(encoding="utf-8"))
shows = d["shows"] if isinstance(d, dict) else d
print(f"total {len(shows)}")
sus = collections.defaultdict(list)

DASH = re.compile(r"[-–—:]\s*[^-–—:]*(?:recommended age|regardless of age|require[sd]? (?:a )?ticket|all guests|babes in arms|no children|fundraiser|meet\s*&\s*greet|vip package|photo op|premium seats?|18\+|21\+|doors? open)", re.I)
QUOTE = re.compile(r"^['‘“\"].+?['’”\"]\s+\w")
NONMUS = re.compile(r"\b(movie|film series|screening|sing-?along|in concert|tribute (?:to|band|show)|drag (?:show|brunch)|stand-?up|comedy night|orchestra plays|symphony|ballet|circus|cirque|magic show|hypnotist)\b", re.I)
PKG = re.compile(r"\b(package|premium experience|meal deal|dinner (?:and|&) show|afternoon tea|hotel)\b", re.I)
PRESENT = re.compile(r"^[A-ZÀ-ÿ][\w .&'’-]{2,45}\s+(?:presents|presenta|présente|präsentiert)\b|Presented By", re.I)

for s in shows:
    t = s.get("title", "") or ""
    if DASH.search(t): sus["A 行銷/須知尾巴"].append(t)
    if QUOTE.match(t): sus["B 引號開頭"].append(t)
    if NONMUS.search(t): sus["C 疑似非音樂劇"].append(t)
    if PKG.search(t): sus["D 套餐/加值"].append(t)
    if PRESENT.search(t): sus["E 主辦前綴/尾綴"].append(t)
    if len(t) > 62: sus["F 超長標題"].append(t)
    if len(t) > 8 and t.upper() == t and re.search(r"[A-Z]{4}", t): sus["G 全大寫"].append(t)
    tn = s.get("tour_name")
    if tn and t and t.lower() not in tn.lower(): sus["H tour_name不含劇名"].append(f"{t}  <tour:{tn}>")
    if not s.get("start_date") and not s.get("end_date"): sus["I 完全無日期"].append(f"{t} @{s.get('city')}({s.get('source')})")
    if s.get("lat") is None: sus["J 無座標"].append(f"{t} @{s.get('city')}")

byvc = collections.defaultdict(list)
for s in shows:
    byvc[((s.get("venue") or "").lower(), (s.get("city") or "").lower().split(",")[0])].append(s)
for (v, c), ls in byvc.items():
    if len(ls) < 2 or not v: continue
    for i in range(len(ls)):
        for j in range(i + 1, len(ls)):
            a, b = ls[i], ls[j]
            if a["group"] == b["group"]: continue
            r = SequenceMatcher(None, a["group"], b["group"]).ratio()
            if r > 0.66:
                sus["K 同館近似重複"].append(f"{a['title']!r} vs {b['title']!r} @{v[:26]} (r={r:.2f})")

for k in sorted(sus):
    items = sorted(set(sus[k]))
    print(f"\n== {k} ({len(items)}) ==")
    for t in items:
        print("  ", t[:120])
