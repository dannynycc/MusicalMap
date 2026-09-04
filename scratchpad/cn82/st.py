# -*- coding: utf-8 -*-
"""一行式進度:生成 / 已判讀 / 待讀。verify_log.summary() 現在太長,日常看這個就好。"""
import io, json, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
B = "scratchpad/cn82"
log = json.load(io.open(B + "/verify_log.json", encoding="utf-8"))
# 🚨 底線開頭的鍵是【註記】(_overturned_suspicions),值不是 {verdict,basis,todo} 的形狀。
#    把註記混進「以組名為鍵」的集合裡,會讓每一個讀取端都炸掉(st.py 與 verify_log.summary
#    兩支都中)。這裡與 summary() 用同一條排除規則。
log = {k: v for k, v in log.items() if not k.startswith("_")}
tot = {"ok": 0, "fix": 0, "reject": 0}
for gg in log.values():
    for v in gg.values():
        tot[v["verdict"]] = tot.get(v["verdict"], 0) + 1
for suf, lang in [("zht", "zh-hant"), ("en", "en")]:
    rows = json.load(io.open("%s/regen_%s.json" % (B, suf), encoding="utf-8"))
    order = json.load(io.open("%s/regen_%s_order.json" % (B, suf), encoding="utf-8"))
    un = [g for i, g in enumerate(order) if i < len(rows) and lang not in log.get(g, {})]
    print("%-8s 生成 %2d/69   待讀 %d   %s" % (lang, len(rows), len(un), un[:6]))
print("通讀 %d 篇 / %d 組  →  ok %d / fix %d" %
      (sum(tot.values()), len(log), tot["ok"], tot["fix"]))
