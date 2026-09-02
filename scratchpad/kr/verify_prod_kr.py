# -*- coding: utf-8 -*-
"""驗正式站:5 檔非音樂劇真的不見了、被推翻誤判的 3 檔真的還在、韓國連結真的能開。"""
import io, json, sys, urllib.request, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) MusicalMap-verify"}
def get(u):
    with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))
rows = get("https://themusicalmap.com/data/variants/shows.en.json")["shows"]
groups = set(r.get("group") for r in rows)
print("正式站場次 %d,組 %d" % (len(rows), len(groups)))
print()
print("【應已排除】")
for g in ("spotlight", "hunky show", "touch five", "club seolhwa",
          "2026년 전주브랜드공연 마당창극 별향단젼이라"):
    print("  %-42s %s" % (g[:42], "❌ 仍在" if g in groups else "✓ 已排除"))
print()
print("【應保留(我推翻自己誤判的)】")
for g in ("음악극 소요유", "벚꽃동산 하얀 집", "let the cheongsachorong shine", "오셀로와 이아고"):
    print("  %-42s %s" % (g[:42], "✓ 保留" if g in groups else "❌ 被誤殺"))
print()
kr = [r for r in rows if (r.get("source") or "").startswith("world.nol")]
dom = [r for r in kr if "tickets.interpark" in (r.get("ticket_url") or "")]
intl = [r for r in kr if "world.nol" in (r.get("ticket_url") or "")]
print("韓國場次 %d:韓國站連結 %d、國際站連結 %d" % (len(kr), len(dom), len(intl)))
bad = 0
for r in (dom[:6] + intl[:6]):
    try:
        s = urllib.request.urlopen(urllib.request.Request(r["ticket_url"], headers=UA), timeout=20).status
    except Exception as e:                                   # noqa: BLE001
        s = str(e)[:18]
    if s != 200:
        bad += 1
        print("  ❌ %s %s" % (r["title"][:30], s))
    time.sleep(0.3)
print("正式站連結抽驗 12 條,非 200:%d" % bad)
