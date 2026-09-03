# -*- coding: utf-8 -*-
"""從 p4_ledger 產生 px_gen 用的重生成 prompt。

🚨 為什麼要這支(2026-09-03):
逐齣人工比對時一再發現同一種錯 —— Perplexity 拿【原著/小說/名作】的情節與角色來填,
而不是這個【製作本身】的官方文案(현남동 서점寫進小說才有的 지미/상수/민철、
파랑새寫成原著版「仙女生病的女兒」而非本製作的「생병的미틸」、청사초롱憑空生出五名員工)。
修法是把官方逐字原文 + 官方角色表 + 我的查證清單一起放進 prompt,並明令只准用這些內容。

用法: python scratchpad/kr/mk_regen.py <ledger_key> [<ledger_key> ...] -o <out_list.json>
"""
import io
import json
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

LEDGER = "scratchpad/kr/p4_ledger.json"
TODO = "scratchpad/kr/syn_todo.json"

HEAD = ("「{ko}」 — {origin}, staged at {venue} in {city}, {year}. "
        "Below is this production's OWN official plot text, transcribed verbatim from its official "
        "programme page (it is published only as an image, which is why web search cannot find it). "
        "Base your synopsis ONLY on this text: do not substitute the plot of any other work — not the "
        "novel, play, film, or legend it is adapted from — and do not invent characters or events that "
        "are absent from it. ")


def build(key, led, todo):
    v = led[key]
    t = todo[v["code"]]
    origin = ("produced by %s" % t["producer"]) if t.get("producer") else "a Korean production"
    q = HEAD.format(ko=t.get("ko") or key, origin=origin[:120],
                    venue=t.get("venue") or "?", city=t.get("city") or "?", year=t.get("year") or "2026")
    q += "OFFICIAL TEXT: 《%s》 " % (v.get("official_plot") or "").strip()
    if v.get("characters"):
        q += "OFFICIAL CHARACTER LIST — these are the ONLY characters in this production: 《%s》 " % v["characters"].strip()
    if v.get("checklist"):
        # 清單是我逐張讀官方圖後寫下的「必含/不可寫」事實,直接當成硬約束餵進去
        q += ("VERIFIED FACTS about this production (each was read off the official programme images; "
              "your synopsis must not contradict any of them): 《%s》 " % " | ".join(v["checklist"]))
    return q


def main():
    argv = sys.argv[1:]
    out = None
    if "-o" in argv:
        i = argv.index("-o")
        out = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    led = json.load(io.open(LEDGER, encoding="utf-8"))["shows"]
    todo = {r["code"]: r for r in json.load(io.open(TODO, encoding="utf-8"))}
    rows = []
    for k in argv:
        if k not in led:
            print("✗ 帳本沒有這個鍵:", k)
            return 1
        q = build(k, led, todo)
        rows.append(q)
        print("✔ %-34s prompt %d 字" % (k[:34], len(q)))
    if out:
        json.dump(rows, io.open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("→ 寫出", out)
    return 0


raise SystemExit(main())
