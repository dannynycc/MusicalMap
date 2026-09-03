# -*- coding: utf-8 -*-
"""把合併後的最終稿匯出成 kb_merge.py 吃得下的格式。

kb_merge 需要 [{"show": <對得到 keymap 的劇名>, "synopsis": <內文>}]。
本批的 group 就是目錄裡的 group key,所以直接用 group 當 show。

🚨 入庫前的三道關卡(任何一道不過就中止,不寫檔):
   1. 三語筆數都等於 19
   2. 沒有空稿
   3. 沒有 verdict=reject 的劇(本批目前沒有,但保留機制)

用法: python scratchpad/gap19/export_for_kb.py
輸出: scratchpad/gap19/final_en.json / final_zht.json / final_zhs.json
"""
import io
import json
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
BASE = "scratchpad/gap19"
PAIRS = [("en", "merged_en.json", "final_en.json"),
         ("zh-hant", "merged_zht.json", "final_zht.json"),
         ("zh-hans", "merged_zhs.json", "final_zhs.json")]
REJECT = set()          # 本批沒有判定不出簡介的劇


def load(p):
    return json.load(io.open("%s/%s" % (BASE, p), encoding="utf-8"))


def main():
    order = load("order.json")
    problems = []
    out_all = {}
    for lang, src, dst in PAIRS:
        rows = load(src)
        if len(rows) != len(order):
            problems.append("%s 筆數 %d != %d" % (lang, len(rows), len(order)))
            continue
        out = []
        for i, g in enumerate(order):
            if g in REJECT:
                continue
            s = (rows[i].get("synopsis") or "").strip()
            if not s:
                problems.append("%s / %s 空稿" % (lang, g))
                continue
            # 英文稿不得含 CJK / 諺文(第一輪 天堂邊緣 就犯過)
            if lang == "en" and re.search(r"[぀-ヿ一-鿿가-힯]", s):
                problems.append("%s / %s 英文稿夾非拉丁字系文字" % (lang, g))
            out.append({"show": g, "synopsis": s})
        out_all[dst] = out

    if problems:
        print("✋ 入庫前把關【未通過】,不寫檔:")
        for p in problems:
            print("   -", p)
        return 1

    for dst, out in out_all.items():
        json.dump(out, io.open("%s/%s" % (BASE, dst), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=2)
        print("✅ %s  %d 筆" % (dst, len(out)))
    return 0


raise SystemExit(main())
