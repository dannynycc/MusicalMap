# -*- coding: utf-8 -*-
"""三語逐組對照工具(西葡第二批)。

用途:英文那一輪已經逐組對過官方原文並修正,所以英文是【已驗過的基準】。
繁中/簡中是各自獨立生成的,錯誤不會跟英文重疊(這是既有教訓),
所以要拿【同一份官方原文 + 已驗過的英文】去對,不能驗一語當三語。

用法:
  python scratchpad/eses/cmp3.py                 # 列出各語進度與字數異常
  python scratchpad/eses/cmp3.py <關鍵字>        # 印出該組的官方原文重點 + 三語全文
"""
import io, json, os, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

B = "scratchpad/eses/b2/"
FILES = {"en": "out_en.json", "zh-hant": "out_zht.json", "zh-hans": "out_zhs.json"}
RANGE = {"en": (220, 340), "zh-hant": (400, 450), "zh-hans": (400, 450)}


def size(lang, text):
    return len(text.split()) if lang == "en" else len(text)


def load(lang):
    path = B + FILES[lang]
    if not os.path.exists(path):
        return {}
    return {r["show"]: r["synopsis"] for r in json.load(io.open(path, encoding="utf-8"))}


def keymap():
    return {lbl: g for g, lbl in
            json.load(io.open("scratchpad/eses/b2_keymap.json", encoding="utf-8"))}


def prefetch():
    return json.load(io.open("scratchpad/eses/prefetch.json", encoding="utf-8"))


def overview():
    km = keymap()
    print("組別總數 %d" % len(km))
    for lang in FILES:
        d = load(lang)
        lo, hi = RANGE[lang]
        bad = [(k[:40], size(lang, v)) for k, v in d.items()
               if not (lo <= size(lang, v) <= hi)]
        print("  %-8s 已生成 %2d / %d   字數超出 %d–%d 的:%s"
              % (lang, len(d), len(km), lo, hi, bad if bad else "無"))


def detail(q):
    km = keymap()
    hits = [lbl for lbl in km if q.lower() in lbl.lower() or q.lower() in km[lbl]]
    if not hits:
        print("查無:%s" % q)
        return
    pre = prefetch()
    for lbl in hits:
        g = km[lbl]
        p = pre.get(g, {})
        print("=" * 78)
        print("group: %s" % g)
        print("=" * 78)
        print("【官方原文】")
        print(p.get("official_plot", "⚠ 未取得"))
        if p.get("key_facts"):
            print("\n【查核重點】")
            for k in p["key_facts"]:
                print("  - " + k)
        for lang in FILES:
            d = load(lang)
            if lbl in d:
                print("\n" + "-" * 78)
                print("[%s] %d" % (lang, size(lang, d[lbl])))
                print("-" * 78)
                print(d[lbl])
        print()


if len(sys.argv) > 1:
    detail(" ".join(sys.argv[1:]))
else:
    overview()
