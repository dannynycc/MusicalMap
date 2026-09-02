# -*- coding: utf-8 -*-
"""把我【本人讀官方詳情圖】得到的 ground truth 逐齣寫進 P4 帳本。

用法: python scratchpad/kr/p4_add.py <entry.json>
entry.json = 單筆 dict,鍵見 p4_ledger.json 的 _schema。
工具只負責寫檔;讀圖與判斷全是我本人做的。
"""
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
P = "scratchpad/kr/p4_ledger.json"
BASE = {
    "_note": "P4 三語簡介的 ground truth 帳本(2026-09-02 起)。每一筆的 official_plot 都是我本人"
             "用 Read 打開官方詳情長圖、逐字抄下來的 —— 61 齣裡有 60 齣的公演介紹【整段是圖】,"
             "純文字來源(新聞/維基/售票頁文字/agent)結構上拿不到。checklist 是我從官方原文抽出的"
             "查核點,用來對 Perplexity 的三語產出;依 SOP §1 絕不餵進生成 prompt。",
    "_schema": {
        "code": "Interpark goodsCode",
        "img": "我讀的那幾張切片檔名",
        "official_plot": "官方 줄거리/SYNOPSIS 的【逐字】韓文原文(不是我的翻譯)",
        "characters": "官方 등장인물 欄逐字",
        "checklist": "我從官方原文抽出的查核點",
        "note": "我讀圖當下的判斷與疑點",
    },
    "shows": {},
}
d = json.load(io.open(P, encoding="utf-8")) if os.path.exists(P) else BASE
e = json.load(io.open(sys.argv[1], encoding="utf-8"))
d["shows"][e["group"]] = e
json.dump(d, io.open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("帳本已記 %s(共 %d 筆)" % (e["group"], len(d["shows"])))
