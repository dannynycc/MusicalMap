# -*- coding: utf-8 -*-
"""第一層機械把關:拿生成稿對帳本查【硬性禁忌】與【角色名漂移】。

這【不取代】逐篇人工通讀(SOP:自動掃描會一再誤放),只是先把最容易犯的錯撈出來,
讓人工通讀時知道該盯哪裡。

三種檢查:
 1. forbidden  —— 帳本註明「寫了就是錯」的詞(例:Na prochach 的 Sackler/Purdue)
 2. typo       —— 文中專名與官方角色表【近似但不相等】= 拼錯官方角色名
                  (實測第一篇就把官方 Barker 寫成 Baker)
 3. unknown    —— 文中專名【不在】官方角色表 = 可能是自己編的角色/地名

用法: python scratchpad/gap19/gate.py <out_en.json|out_zht.json|out_zhs.json>
"""
import difflib
import io
import json
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
BASE = "scratchpad/gap19"

FORBIDDEN = {
    "na prochach": ["Sackler", "Purdue", "OxyContin", "薩克勒", "萨克勒", "普渡"],
    "romeo i julia": ["Roméo et Juliette", "Presgurvic"],
    # 以下幾齣官方只給泛稱,英文原版/原著角色名【未經本製作證實】,寫了就是推定
    "blood brothers": ["Johnstone", "Mickey", "Eddie", "Lyons", "Linda", "Sammy"],
    "carrie": ["Sue Snell", "Tommy Ross", "Chris Hargensen", "Billy Nolan", "Gardner",
               "Margaret White"],
    "charlie brown christmas": ["Sally", "Schroeder", "Pigpen", "Pig-Pen", "Peppermint Patty",
                                "Marcie", "Woodstock"],
    "on your feet": ["Consuelo", "Fajardo"],
}
GENERIC_ONLY = {"blood brothers", "carrie", "on your feet", "charlie brown christmas",
                "caperucita roja", "天堂邊緣"}

# 一般英文句首字/通用名詞,不是角色名
STOP = set("""The This That These Those When While After Before Their Her His But And Or In On At
As For With From She He It They We You There What Who How Why One Two Three Four Five Act Scene
Meanwhile Later Then Now Today Tonight Yet Still Both Each Every All Some No Not Only Even
Warsaw Poland Polish Hungary Hungarian Budapest Barcelona Catalan Catalonia Spain Mexico Mexican
America American United States Maine Florida York Miami Christmas New Broadway West End
Kyoto Tokyo Osaka Japan Japanese Korea Taiwan Taipei Kaohsiung London England English
January February March April May June July August September October November December
Monday Tuesday Wednesday Thursday Friday Saturday Sunday
God Lord Mr Mrs Ms Dr Sir Madam Act One Two Finale Prologue Epilogue""".split())


def official_names(g, led):
    """從帳本 characters 欄抽出官方角色專名(拉丁字母、長度>=3)。"""
    c = led.get(g, {}).get("characters") or ""
    c = re.sub(r"[一-鿿（）()「」『』：:，,、。；;·【】]+", " ", c)
    toks = re.findall(r"[A-ZŁŚŻŹĆŃÓÄÖÜÁÉÍÓÚÀÈÌÒÙÂÊÎÔÛÃÕÇ][\w'’\-]{2,}", c, re.UNICODE)
    drop = {"Teatr", "Syrena", "Obsada", "Studio", "Buffo", "Condal", "Theatre", "Stage",
            "Vígszínház", "Déryné", "Társulat"}
    return {t for t in toks if t not in drop}


def text_names(txt):
    """抓文中專名候選:排除句首(前面是 . ! ? 或字串開頭)。"""
    out = []
    for m in re.finditer(r"[A-ZŁŚŻŹĆŃÓÄÖÜÁÉÍÓÚÀÈÌÒÙÂÊÎÔÛÃÕÇ][\w'’\-]{2,}", txt, re.UNICODE):
        s = m.start()
        prev = txt[max(0, s - 2):s]
        if s == 0 or re.search(r"[.!?][\s\"'“”]*$", prev):
            continue          # 句首,可能只是一般字
        # 🚨 只剝所有格 's / ’s,不可用 rstrip("'’s") —— 那會把字尾的 s 也吃掉,
        #    把 Harris'→Harri、Parys'→Pary、Áts→Át、Linus's→Linu 全報成拼錯。
        out.append(re.sub(r"[’']s?$", "", m.group(0)))
    return out


def cast_check(g, txt, led):
    off = official_names(g, led)
    if not off:
        return [], []
    unknown, typo = [], []
    for t in sorted(set(text_names(txt))):
        if t in STOP or t in off:
            continue
        near = difflib.get_close_matches(t, off, n=1, cutoff=0.78)
        if near:
            typo.append("%s→應為 %s" % (t, near[0]))
        else:
            unknown.append(t)
    return unknown, sorted(set(typo))


def main():
    path = sys.argv[1]
    rows = json.load(io.open(path, encoding="utf-8"))
    order = json.load(io.open("%s/order.json" % BASE, encoding="utf-8"))
    led = json.load(io.open("%s/ledger.json" % BASE, encoding="utf-8"))
    print("稿 %d 筆 / 清單 %d 齣\n" % (len(rows), len(order)))
    bad = 0
    for i, g in enumerate(order):
        if i >= len(rows):
            break
        txt = (rows[i].get("synopsis") or "").strip()
        note = []
        if not txt:
            note.append("空稿")
        hits = [w for w in FORBIDDEN.get(g, []) if w.lower() in txt.lower()]
        if hits:
            note.append("🚨禁忌詞 %s" % hits)
        typo, unknown = [], []
        if txt:
            unknown, typo = cast_check(g, txt, led)
        if typo:
            note.append("拼錯官方角色名 %s" % typo)
        if unknown:
            note.append("角色表沒有的專名 %s" % unknown[:10])
        if g in GENERIC_ONLY:
            note.append("官方只給泛稱→整篇需人工確認")
        if note:
            bad += 1
            print("❌ %-30s %s" % (g, " | ".join(note)))
        else:
            print("○  %-30s 機械檢查無異常(仍須人工通讀)" % g)
    print("\n需要人工處理:%d / %d" % (bad, min(len(rows), len(order))))
    return 0


raise SystemExit(main())
