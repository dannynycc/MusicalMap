# -*- coding: utf-8 -*-
"""簡中通讀輔助:把【官方原文】【已校正的繁中】【新生成的簡中】並排。

為什麼這樣讀:繁中那 69 篇已經逐句對過官方原文並修到正確,拿它當基準,
簡中只要出現【事實上的分歧】就是紅旗——比從零盲讀快得多也嚴得多。
🚨 但基準只管【事實】不管【用語】:簡中該有大陸語感,不能拿繁中的台灣用詞去套。

🚨🚨 判「這句是憑空補的」之前,一定要對【整個 prompt】查,不是只對 official_plot ——
   prompt 還包含【身份段】(劇名/創作者/場館/年份,有時也寫了改編來源)。
   2026-09-04 實測:《时光代理人》簡中寫「改编自哔哩哔哩同名国产动画」,那句不在 official_plot 裡,
   我差點當幻覺刪掉;查過才發現【身份段本身就寫著它】,帳本 note 也記著是我從官方物料讀來的。
   → 本檔會一併印出身份段,判斷前先看它。

用法: python scratchpad/cn82/cmp3.py [起始序號] [幾組]
"""
import io
import json
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
B = "scratchpad/cn82"
led = json.load(io.open(B + "/ledger.json", encoding="utf-8"))
zhs = json.load(io.open(B + "/regen_zhs.json", encoding="utf-8"))
zso = json.load(io.open(B + "/regen_zhs_order.json", encoding="utf-8"))
zht = json.load(io.open(B + "/regen_zht.json", encoding="utf-8"))
zto = json.load(io.open(B + "/regen_zht_order.json", encoding="utf-8"))
log = json.load(io.open(B + "/verify_log.json", encoding="utf-8"))

start = int(sys.argv[1]) if len(sys.argv) > 1 else 0
n = int(sys.argv[2]) if len(sys.argv) > 2 else 3
todo = [g for i, g in enumerate(zso) if i < len(zhs) and "zh-hans" not in log.get(g, {})]
for g in todo[start:start + n]:
    e = led[g]
    print("=" * 74)
    print("【組】", g, "| title_en:", e.get("title_en"))
    plot = (e.get("official_plot") or "").strip()
    ext = ((e.get("external_plot") or {}).get("text") or "").strip()
    print("--官方原文--")
    print((plot or ("(官方無,外部來源)" + ext))[:820])
    ch = (e.get("characters") or "")
    if ch:
        print("--官方角色--")
        print(ch[:420])
    # 身份段(prompt 的前綴)——判「憑空補」之前必看
    try:
        lst = json.load(io.open(B + "/regen_zhs_list.json", encoding="utf-8"))
        ident = lst[zso.index(g)].split(" —— ")[0]
        print("--身份段(prompt 前綴,判憑空補前必看)--")
        print(ident[:300])
    except Exception:
        pass
    print("--已校正的繁中(基準)--")
    print(zht[zto.index(g)]["synopsis"])
    print("--新生成的簡中--")
    print(zhs[zso.index(g)]["synopsis"])
