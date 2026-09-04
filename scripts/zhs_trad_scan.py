# -*- coding: utf-8 -*-
"""簡中(zh-hans)稿件裡的【繁體字殘留】掃描。

為什麼需要:2026-09-04《哪吒》簡中稿寫出「鬧海抗爭」「蓮花重生」——全是繁體。
成因不是模型亂寫,而是【帳本裡那一組的官方資料是用繁體存的】,而 prompt 又要求
「專有名詞一字不改照抄」,模型照做了。所以這個錯只會出現在【資料來源是繁體】的組,
其他 69 組一個都沒有 —— 靠抽樣是抓不到的,必須全掃。

🚨 OpenCC 的 t2s 有【誤報】,不可無腦照著改:
   吒 → 咤   哪吒繁簡同形,官方與教育部辭典都寫「哪吒」;跟著轉反而錯。
   其餘誤報若日後遇到,加進 SKIP 並在這裡寫明理由,不要靜默略過。

用法:
    python scripts/zhs_trad_scan.py <檔.json> [...]      # 報告(不改檔)
"""
import io
import json
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# 已知誤報:字本身在簡體正字裡就是這個寫法,t2s 卻仍會轉
SKIP = {"吒"}


def main():
    from opencc import OpenCC
    t2s = OpenCC("t2s").convert
    rc = 0
    for path in sys.argv[1:]:
        rows = json.load(io.open(path, encoding="utf-8"))
        order = json.load(io.open(path.replace(".json", "_order.json"), encoding="utf-8"))
        bad = 0
        for i, r in enumerate(rows):
            t = r.get("synopsis") or ""
            hits = sorted({c for c in t if t2s(c) != c and c not in SKIP})
            if hits:
                bad += 1
                rc = 1
                where = []
                for c in hits:
                    j = t.index(c)
                    where.append("%s→%s(…%s…)" % (c, t2s(c), t[max(0, j - 6):j + 7]))
                print("❌ %-16s %s" % (order[i], " | ".join(where)))
        print("%s → %d/%d 篇有繁體字殘留" % (path, bad, len(rows)))
    return rc


raise SystemExit(main())
