# -*- coding: utf-8 -*-
import io, sys, json, urllib.request
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) MusicalMap-verify"}
def get(u):
    with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))
base = "https://themusicalmap.com/data/"
shows = get(base + "variants/shows.zh-hant.json")
rows = shows.get("shows", shows)
print("正式站場次總數 %d" % len(rows))
def g(name):
    return [r for r in rows if (r.get("group") or "") == name]
print()
for name in ("murder for two", "assassinat per a dos", "blood brothers", "germans de sang", "urinetown"):
    rs = g(name)
    print("%-22s %d 場" % (name, len(rs)))
    for r in rs:
        print("     %-22s | tour_name=%-24s | %-18s | %s~%s"
              % (r.get("title", "")[:22], str(r.get("tour_name"))[:24],
                 r.get("tag"), r.get("start_date"), r.get("end_date")))
print()
for r in rows:
    if (r.get("group") or "").startswith("la opera de los tres"):
        print("三便士 迄日 = %s (應為 2026-11-06) end_rolling=%s" % (r.get("end_date"), r.get("end_rolling")))
syn = get(base + "synopses/zh-hant.json")
s = syn.get("syn", syn)
print()
for k, need, bad in (("a media luz", "布宜諾斯艾利斯", "酒吧"),
                     ("mi padre sabina y yo", "第三位主角", "剛與女友分手"),
                     ("murder for two", "惠特尼", None)):
    t = (s.get(k) or {}).get("zh") or ""
    ok = (need in t) and (bad is None or bad not in t)
    print("%-22s %s  含「%s」=%s  %s" % (k, "OK " if ok else "!! ", need, need in t,
          ("不含「%s」=%s" % (bad, bad not in t)) if bad else ""))
print()
print("孤兒鍵 assassinat per a dos 仍在?", "assassinat per a dos" in s)
