# -*- coding: utf-8 -*-
"""產生 data/synopses_verification.json 的本批條目(韓國 55 齣)。

🚨 分級一律【只數獨立於主辦方的來源】。
p4_ledger 的 sources 有很多是【同一張官方詳情圖的不同段落】(海報/SYNOPSIS/CAST/INFORMATION),
依 SOP §3.1 規則一,同源不算互相佐證。先前我把「5 源、7 源」直接當成多源交叉是錯的,
本檔改用關鍵字把官方段落與外部來源分開計算:

  external_multisource=True  ≥2 個獨立外部來源
  confidence high/medium/low 依外部來源數 2+/1/0

用法: python scratchpad/kr/mk_verification.py [--write]
不加 --write 只印統計,不動 data/。
"""
import io
import json
import re
import sys
import collections

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
BASE = "scratchpad/kr"
TARGET = "data/synopses_verification.json"
BATCH = "kr-methodB-2026-09-03"
DATE = "2026-09-03"

# 主辦方/售票通路一律視為【官方同源】
OFFICIAL = re.compile(
    r"官方|官網|詳情圖|詳情頁|詳情長圖|海報|Interpark|인터파크|NOL|yanolja|world\.nol|tickets\.|"
    r"公演資料|公演자료|시놉시스|kkyht|제작|Instagram 官方|보도자료|캐스팅區|goods/")
EXTERNAL = re.compile(
    r"나무위키|namu|뉴스|일보|타임즈|포커스|더뮤지컬|themusical|PLAY ?DB|playdb|CNB|뉴스테이지|"
    r"여성동아|디시|블로그|후기|리뷰|kukak21|문화체육관광부|공연포털|wikipedia|維基|德文維基|OTR|"
    r"콘테스트|contestkorea|티스토리|tistory|Facebook|아츠리뷰|kimhyungjun|관람후기|OhmyNews|"
    r"오마이|치악뉴스|시사줌|서울문화투데이|디지스트|전기저널|아트인사이트|kmingky|TV리포트|Instagram")


def load(p):
    return json.load(io.open(p, encoding="utf-8"))


def main():
    led = load("%s/p4_ledger.json" % BASE)["shows"]
    log = load("%s/verify_log.json" % BASE)["shows"]
    _todo = load("%s/syn_todo.json" % BASE)
    todo = {r["code"]: r for r in _todo}
    by_group = {r.get("group"): r for r in _todo}
    km = {t: g for g, t in load("%s/keymap_final.json" % BASE)}

    out, tally = {}, collections.Counter()
    for k, v in led.items():
        code = v["code"]
        rec = log.get(code, {})
        if rec.get("verdict") == "reject":
            continue
        # 🚨 同一齣可能有多個場次代碼(例:someday 帳本記 24007874、syn_todo 是 26010475),
        #    code 對不到時回退用 ledger key == syn_todo.group 比對。
        t = todo.get(code) or by_group.get(k) or {}
        group = km.get(t.get("title_en"))
        if not group:
            print("  ✗ 找不到 group:", k, code, t.get("title_en")); continue
        srcs = v.get("sources") or []
        # 只把【開頭就是「官方…」】的條目算成主辦方同源;像「NOL 관람후기」「PlayDB 出演表」
        # 這種掛在售票通路上的【觀眾評論/第三方資料庫】仍是獨立來源,不可誤判為官方。
        ext = [s for s in srcs
               if EXTERNAL.search(s) and not re.match(r"^\s*(官方|Official)", s)]
        off = [s for s in srcs if s not in ext]
        n = len(ext)
        conf = "high" if n >= 2 else ("medium" if n == 1 else "low")
        tier = "多源交叉" if n >= 2 else ("單一外部+官方" if n == 1 else "僅官方原文")
        tally[tier] += 1
        note = "官方詳情圖由本人逐張讀出並逐句比對三語"
        if v.get("external_search"):
            note += ";已實搜確認查無獨立外部來源(查詢字串記於 p4_ledger.external_search)"
        if rec.get("verdict", "").startswith("regenerate") or rec.get("_regen"):
            note += ";因原稿寫成他作而依官方原文重新生成"
        out[group] = {
            "method": "B", "date": DATE, "langs": ["en", "zh-hant", "zh-hans"],
            "sources": "官方逐字 %d 段 + 獨立外部來源 %d 個" % (len(off), n),
            "external_multisource": n >= 2,
            "external_source_count": n,
            "confidence": conf,
            "errors_fixed": len(rec.get("errors_fixed") or []),
            "batch": BATCH,
            "note": note,
        }
    print("本批可入庫 %d 組" % len(out))
    for t, c in tally.most_common():
        print("   %-14s %d" % (t, c))

    if "--write" in sys.argv:
        d = load(TARGET)
        d["verified"].update(out)
        json.dump(d, io.open(TARGET, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("→ 已寫入 %s(全庫 %d 組)" % (TARGET, len(d["verified"])))
    else:
        print("(未加 --write,沒有寫檔)")
    return 0


raise SystemExit(main())
