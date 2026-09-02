# -*- coding: utf-8 -*-
"""韓國新進 69 組:第一關「這到底是不是音樂劇」的分流。

為什麼要有這一支
----------------
2026-09-02 v2.107.0 拿掉 Interpark 的 globalType=EN 之後,韓國一口氣進了 69 組,
但「是不是音樂劇」一項都沒查過就直接標成韓國原創、進了目錄。
使用者要求的順序是:**先驗是不是音樂劇 → 是的話才往下追分類/劇情/標題**。

判別訊號從哪來(全部來自來源本身,不是我猜的)
--------------------------------------------
⚠ 最重要的一點:`scrapers/interpark.py` 的 clean_title() 會把「뮤지컬」前綴洗掉,
  而那正是最強的判別訊號。所以這裡一律回頭讀 API 的【原始】goodsName / subGoodsName。
  (實例:我們目錄裡叫「오셀로와 이아고」,看起來像莎劇話劇,原名其實是
   「뮤지컬 〈오셀로와 이아고〉」—— 憑清洗後的標題判斷會誤殺。)

  MUSICAL  : 原始名含 뮤지컬 / musical → 來源自己說是音樂劇
  NOT      : 含 음악극(音樂劇場,韓國分類上與 뮤지컬 並列)/ 콘서트 / 연극 /
             창극·마당창극(傳統唱劇)/ 국악 / 오페라 → 不是 뮤지컬
  CHECK    : 兩者都沒有 → 必須人工查證,不得預設為音樂劇

subGenreName(來源子類)另外標出來:
  License = 引進授權劇 → 就算是音樂劇,也不該標「韓國原創」
  Original/visiting concert = 演唱會 → 根本不是音樂劇
"""
import io
import json
import re
import subprocess
import sys
from collections import Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

BASE = "751b57e4cf"          # 今天第一次改動之前的 shows.json

MUSICAL = re.compile(r"뮤지컬|musical", re.I)
NOTMUS = re.compile(r"음악극|콘서트|concert|연극|창극|국악|오페라|opera|무용|리사이틀")


def main():
    raw = json.load(io.open("scratchpad/kr/nol_raw.json", encoding="utf-8"))
    by_code = {str(x.get("goodsCode")): x for x in raw}

    old = json.loads(subprocess.run(["git", "show", BASE + ":data/shows.json"],
                                    capture_output=True).stdout.decode("utf-8"))["shows"]
    og = set(r["group"] for r in old)
    new = json.load(io.open("data/shows.json", encoding="utf-8"))["shows"]

    rows, seen = [], set()
    for r in new:
        g = r["group"]
        if g in og or g in seen:
            continue
        if not (r.get("source") or "").startswith("world.nol"):
            continue
        seen.add(g)
        code = re.sub(r"^ip-", "", r["id"])
        x = by_code.get(code) or {}
        rawname = (x.get("goodsName") or "") + " ｜ " + (x.get("subGoodsName") or "")
        if MUSICAL.search(rawname):
            verdict = "MUSICAL"
        elif NOTMUS.search(rawname):
            verdict = "NOT"
        else:
            verdict = "CHECK"
        rows.append({
            "group": g, "our_title": r.get("title"), "raw": rawname.strip(" ｜"),
            "sub": (x.get("subGenreName") or "?"), "verdict": verdict,
            "place": r.get("venue"), "city": r.get("city"),
            "start": r.get("start_date"), "end": r.get("end_date"),
            "code": code, "running": x.get("runningTime"),
            "corp": x.get("corporationName"),
        })

    print("今天新進、來自 NOL 的組:%d" % len(rows))
    print("分流結果:", dict(Counter(r["verdict"] for r in rows)))
    print("來源子類:", dict(Counter(r["sub"] for r in rows)))
    print()
    for v in ("NOT", "CHECK", "MUSICAL"):
        sel = [r for r in rows if r["verdict"] == v]
        print("=" * 78)
        print("【%s】%d 組" % (v, len(sel)))
        for r in sorted(sel, key=lambda x: x["group"]):
            print("  %-30s | %-11s | %s" % (r["group"][:30], r["sub"][:11], r["raw"][:60]))
        print()

    json.dump(rows, io.open("scratchpad/kr/triage.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("→ scratchpad/kr/triage.json")
    return 0


raise SystemExit(main())
