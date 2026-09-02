# -*- coding: utf-8 -*-
"""快篩:今天新進的韓國節目,到底是不是音樂劇。

為什麼可以用「韓文官方名稱」快篩
--------------------------------
韓國的演出習慣把類型寫進正式名稱:「뮤지컬 〈X〉」「음악극 X」「창작가무극 X」
「마당창극 X」「쇼뮤지컬 X」「뮤지컬펍 X」。這是**製作方自己的命名**,
跟 Interpark 的分類欄位是兩回事 —— 後者我們本來就是用 genreType=MUSICAL 拉的,
拿它來驗「是不是音樂劇」等於恆真、零資訊。

⚠ 我們自己的 clean_title() 會把「뮤지컬」前綴洗掉,所以一定要回頭讀
   tickets.interpark.com summary API 的原始 goodsName(存在 scratchpad/kr/genre.json)。
   實例:目錄裡叫「오셀로와 이아고」看起來像莎劇話劇,韓文原名是「뮤지컬 〈오셀로와 이아고〉」。

判定等級(誠實分級,不把粗篩說成已查證)
  YES    製作方自己冠了 뮤지컬 / musical → 快篩通過
  NO     冠的是 음악극 / 창극 / 콘서트 / 뮤지컬펍(酒吧入場券)→ 不是音樂劇
  GREY   冠的是 가무극 / 쇼뮤지컬 等邊界類型 → 要人工決定收不收
  ASK    名稱裡沒有任何類型字 → 快篩無法判定,需獨立來源
"""
import io
import json
import re
import subprocess
import sys
from collections import Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

BASE = "751b57e4cf"

YES = re.compile(r"뮤지컬|musical", re.I)
PUB = re.compile(r"뮤지컬펍")                       # 音樂劇酒吧 = 入場券,不是製作
NO = re.compile(r"음악극|창극|판소리|콘서트|concert|연극|국악|오페라|무용")
GREY = re.compile(r"가무극|쇼뮤지컬")


def verdict(name):
    if PUB.search(name):
        return "NO", "뮤지컬펍(酒吧入場券,非製作)"
    if GREY.search(name):
        return "GREY", GREY.search(name).group(0)
    if NO.search(name):
        return "NO", NO.search(name).group(0)
    if YES.search(name):
        return "YES", "製作方自冠 뮤지컬/Musical"
    return "ASK", "名稱無類型字"


def main():
    g = {r["group"]: r for r in json.load(io.open("scratchpad/kr/genre.json", encoding="utf-8"))}
    old = json.loads(subprocess.run(["git", "show", BASE + ":data/shows.json"],
                                    capture_output=True).stdout.decode("utf-8"))["shows"]
    og = set(r["group"] for r in old)
    new = json.load(io.open("data/shows.json", encoding="utf-8"))["shows"]

    rows, seen = [], set()
    for r in new:
        grp = r["group"]
        if grp in seen or not (r.get("source") or "").startswith("world.nol"):
            continue
        seen.add(grp)
        d = g.get(grp) or {}
        name = " ".join(filter(None, [d.get("goodsName"), d.get("subGoodsName")]))
        v, why = verdict(name)
        rows.append({"group": grp, "new_today": grp not in og, "ko_name": name,
                     "sub": d.get("genreSubName"), "verdict": v, "why": why,
                     "tag": r.get("tag"), "code": d.get("goodsCode")})

    today = [r for r in rows if r["new_today"]]
    print("今天新進的韓國組:%d(目錄裡 NOL 全部 %d)" % (len(today), len(rows)))
    print("快篩:", dict(Counter(r["verdict"] for r in today)))
    print()
    for v, label in (("NO", "❌ 不是音樂劇"), ("GREY", "⚠ 邊界類型,要人工決定"),
                     ("ASK", "❓ 快篩判不出,需獨立來源"), ("YES", "✅ 製作方自己冠了 뮤지컬")):
        sel = [r for r in today if r["verdict"] == v]
        print("=" * 76)
        print("%s —— %d 組" % (label, len(sel)))
        for r in sorted(sel, key=lambda x: x["group"]):
            print("  %-28s | %-46s | %s" % (r["group"][:28], r["ko_name"][:46], r["why"]))
        print()

    # 分類層(第二關,只對確定是音樂劇的才有意義)
    lic = [r for r in rows if r["sub"] == "라이선스" and r["tag"] == "韓國原創"]
    print("=" * 76)
    print("【分類錯誤】Interpark 標 라이선스(引進授權)、我們卻標「韓國原創」:%d 組" % len(lic))
    for r in lic:
        print("  %-28s | %s" % (r["group"][:28], r["ko_name"][:52]))

    json.dump(rows, io.open("scratchpad/kr/quick.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("\n→ scratchpad/kr/quick.json")
    return 0


raise SystemExit(main())
