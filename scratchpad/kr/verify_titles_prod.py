# -*- coding: utf-8 -*-
"""驗正式站:譯名真的顯示出來、合併真的生效、繁簡差異真的分開。"""
import io, json, sys, urllib.request
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) MusicalMap-verify"}
def get(u):
    with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))
B = "https://themusicalmap.com/data/variants/shows.%s.json"
ht = {r["group"]: r for r in get(B % "zh-hant")["shows"]}
hs = {r["group"]: r for r in get(B % "zh-hans")["shows"]}
en = get(B % "en")["shows"]
print("正式站場次 %d,組 %d" % (len(en), len(set(r["group"] for r in en))))
print()
print("%-34s %-24s %-24s" % ("group", "繁中", "簡中"))
for g in ("7080 뮤지컬 목마와 숙녀", "brahms", "생텍쥐페리", "your letter", "김종욱 찾기",
          "black mary poppins", "origin of species", "쇼뮤지컬 드림하이", "fan letter",
          "6點下班", "음악극 소요유", "베어만 마지막잎새", "welcome to the hyunam dong bookshop",
          "그날들", "썸데이", "gwanghwamun love song", "빨래", "크리스마스 캐럴"):
    a, b = ht.get(g), hs.get(g)
    if not a:
        print("%-34s ❌ 不在目錄" % g[:34]); continue
    print("%-34s %-24s %-24s" % (g[:34], (a.get("cn_annot") or a["title"])[:24],
                                 (b.get("cn_annot") or b["title"])[:24]))
print()
import collections
for g in ("fan letter", "그날들", "썸데이", "6點下班"):
    rs = [r for r in en if r["group"] == g]
    print("%-14s %d 場 | %s" % (g, len(rs), ",".join(sorted(set(r["city"] for r in rs)))[:60]))
print()
syn = get("https://themusicalmap.com/data/synopses/zh-hant.json")
syn = syn.get("syn", syn)
print("西葡新 4 組簡介上線:", [g for g in ("mariana", "es navidad", "monstruos",
                                    "leyendas mexicanas de terror 2")
                       if (syn.get(g) or {}).get("zh")])
