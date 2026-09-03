# -*- coding: utf-8 -*-
"""把三輪產出合併成最終稿。

三個來源,後者覆蓋前者:
  out_*.json     第一輪(身份提示,19 齣)
  regen_*.json   第二輪(事實受限,8 齣)—— 英文批通讀抓到的錯
  regen2_*.json  第三輪(事實受限,3 齣)—— 中文批通讀才抓到的錯

🚨 合併結果寫進 merged_*.json,【絕不覆蓋 out_*.json】。
   out_* 是各輪的原始產出記錄,覆蓋掉就無法回溯「哪一輪修好了什麼」;
   而且如果之後有人重跑 px_gen,手動塞進 out_* 的修正會被靜默蓋掉(這個坑踩過)。

用法: python scratchpad/gap19/merge_all.py
"""
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
BASE = "scratchpad/gap19"
LANGS = [("en", "en"), ("zht", "zh-hant"), ("zhs", "zh-hans")]


def load(name):
    p = "%s/%s" % (BASE, name)
    return json.load(io.open(p, encoding="utf-8")) if os.path.exists(p) else None


def main():
    order = load("order.json")
    assert order, "order.json 不存在"
    ok = True
    for short, lang in LANGS:
        base = load("out_%s.json" % short)
        if base is None or len(base) != len(order):
            print("✗ %-8s out_%s.json 缺漏或筆數不符,跳過" % (lang, short))
            ok = False
            continue
        merged = [dict(r) for r in base]
        applied = {}
        # R3 的清單【各語言不同】(見 mk_regen3.py 的 PER_LANG):
        # 英文要修列名單/夾中文字/空稿,中文只要修 caperucita 與 precure 的名字。
        for tag, lf, of in [("R1", "regen_%s.json" % short, "regen_order.json"),
                            ("R2", "regen2_%s.json" % short, "regen2_order.json"),
                            ("R3", "regen3_%s.json" % short,
                             "regen3_order_%s.json" % short)]:
            rows, rorder = load(lf), load(of)
            if rows is None or rorder is None:
                print("   (%s %s 尚未產出,略過)" % (lang, tag))
                ok = False          # 🚨 少一輪重生成就不算齊備,不可印「三語齊備」
                continue
            if len(rows) < len(rorder):
                print("   (%s %s 只跑到 %d/%d,尚未完成)" % (lang, tag, len(rows), len(rorder)))
                ok = False
            for i, g in enumerate(rorder):
                if i >= len(rows):
                    break
                s = (rows[i].get("synopsis") or "").strip()
                if not s:
                    continue
                merged[order.index(g)]["synopsis"] = s
                applied[g] = tag
        empty = [order[i] for i, r in enumerate(merged) if not (r.get("synopsis") or "").strip()]
        json.dump(merged, io.open("%s/merged_%s.json" % (BASE, short), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        print("%-8s merged_%s.json  %d 筆 | 被重生成覆蓋 %d 齣 %s%s" % (
            lang, short, len(merged), len(applied),
            sorted(applied), "  ⚠空稿:%s" % empty if empty else ""))
        if empty:
            ok = False
    print("\n%s" % ("✅ 三語齊備、三輪重生成都已套用,可以進入庫流程"
                    if ok else "⚠ 尚未齊備(有空稿或重生成還沒跑完),【先別入庫】"))
    return 0


raise SystemExit(main())
