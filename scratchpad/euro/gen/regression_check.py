# -*- coding: utf-8 -*-
"""歐陸三語簡介的回歸檢查。改動 out_*.json 後請重跑。

兩組檢查:
  A. 哨兵 —— 「我曾經改錯、後來查證復原」的字串必須still在(防止有人重跑舊規則又改壞)
  B. 禁用 —— 已查證為錯的寫法不可再出現;**必須綁定部別**,因為同一個中譯可能
     在別部是正確的(例:「桑德」在 Änglagård 是把 Zander 誤譯,但在 The Julekalender
     是官方角色 Oluf Sand / Gertrud Sand 的正確譯名)。
用法: python regression_check.py
"""
import json, io, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
EXPECT = {"out_en.json": 51, "out_zht.json": 51, "out_zhs.json": 51}

SENTINEL = {  # 檔案 -> [(部別前綴 or None, 必須存在的字串)]
    "out_en.json": [("A Christmas Carol", "his wife Rose"), ("Saturnin", "named Jirotka"),
                    ("Macskafog", "Cicus"), ("Macskafog", "Poliakoff"),
                    ("Zlatovláska", "Černovláska"), ("A meseautó", "Központi bank")],
    "out_zht.json": [("MADE IN", "瑞奇"), ("Zlatovláska", "草叢"), ("C'era una volta", "'o russo"),
                     ("Änglagård", "贊德"), ("Močál Story", "布拉熱娜"),
                     ("The Julekalender", "桑德")],   # 這裡的桑德是官方 Sand,必須留著
    "out_zhs.json": [("MADE IN", "瑞奇"), ("Metro", "扬"), ("Saturnin", "伊罗特卡"),
                     ("Mindig itt", "拉约什二世"), ("A dzsungel", "图娜"),
                     ("Aggiungi", "亲自打来的电话"), ("Aggiungi", "白鸽"),
                     ("A Padlás", "摆渡人"), ("A Padlás", "鬼魂")],
}
BANNED = {   # 檔案 -> [(部別前綴, 不可出現的字串)]
    "out_en.json": [(None, "a Budapest bank"), (None, "flinke-kindjes-meter"), (None, "Liga tolerance")],
    "out_zht.json": [("C'era una volta", "俄羅斯人"), ("VY NEJSTE", "寬容聯盟"), ("MADE IN", "米基"),
                     ("Änglagård", "桑德"),            # 只有這一部的「桑德」是錯的
                     ("Pippi", "警察克林"), ("Močál Story", "達莎．諾瓦可娃突然失去蹤影")],
    "out_zhs.json": [("C'era una volta", "俄罗斯人"), ("VY NEJSTE", "宽容联盟"), ("MADE IN", "米基"),
                     ("Metro", "雅努什"), ("A dzsungel", "路易"), ("A dzsungel", "梅苏亚"),
                     ("Légy jó", "孤儿"), ("Emil i Lönneberga", "女佣阿尔弗雷德"),
                     ("Anděl Páně", "国王"), ("Snowboar", "姐姐露茜卡")],
}

def load(f):
    return json.load(open(os.path.join(HERE, f), encoding="utf-8"))

def pick(d, pre):
    return [r for r in d if r["show"].startswith(pre)] if pre else d

lines, bad = [], []
for f, exp in EXPECT.items():
    d = load(f)
    short = [r["show"][:34] for r in d if len(r["synopsis"]) < 200]
    lines.append("%-14s %d 筆(預期 %d) 過短:%s" % (f, len(d), exp, short or "無"))
    if len(d) != exp: bad.append("%s 筆數 %d != %d" % (f, len(d), exp))
for f, pairs in SENTINEL.items():
    d = load(f)
    for pre, kw in pairs:
        rs = pick(d, pre)
        if not rs: bad.append("哨兵找不到部別 %s / %s" % (f, pre)); continue
        if not any(kw in r["synopsis"] for r in rs):
            bad.append("哨兵遺失 %s / %s / %s" % (f, pre, kw))
for f, pairs in BANNED.items():
    d = load(f)
    for pre, kw in pairs:
        for r in pick(d, pre):
            if kw in r["synopsis"]:
                bad.append("禁用殘留 %s / %s / %s" % (f, r["show"][:30], kw))
lines.append("結果: %s" % ("全部通過" if not bad else "FAIL"))
for b in bad: lines.append("  [!] " + b)
open(os.path.join(HERE, "_regression_result.txt"), "w", encoding="utf-8").write("\n".join(lines))
sys.exit(1 if bad else 0)
