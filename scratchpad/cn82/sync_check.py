# -*- coding: utf-8 -*-
"""帳本 ↔ 目錄對帳。每次改完 ledger.json 或重跑 build_shows.py 都要跑一次。

🚨 為什麼需要:2026-09-04 發現同一齣戲被建了【兩份】帳本條目 ——
   `q` vs `阿Q与吴妈`、`在那遥远的地方2 0` vs `在那遥远的地方2.0`,
   因為不同輪次分別用了【目錄 group key】與【劇名】當鍵。
   純字串正規化的查重抓不到(`q` 與 `阿q与吴妈` 正規化後完全不同),
   唯一可靠的比對基準是 shows.json 的 group。

檢查四件事:
  1. 目錄有、帳本沒有  → 漏建帳(必須補)
  2. 帳本有、目錄沒有  → 要嘛是已下架/改分類(該有 catalog_status 說明),要嘛就是【鍵打錯】
  3. 帳本鍵不是目錄 group key,但另一個鍵是同一齣 → 重複條目
  4. status 與 official_plot 是否自洽(有劇情卻標 partial,或反之)

用法: python scratchpad/cn82/sync_check.py
"""
import io
import json
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

LEDGER = "scratchpad/cn82/ledger.json"
SHOWS = "data/shows.json"
TAGS = ("中國原創", "韓國原創")   # borderline/桑塔露琪亚 改標韓國後仍屬本批


def main():
    led = json.load(io.open(LEDGER, encoding="utf-8"))
    entries = {k: v for k, v in led.items() if not k.startswith("_")}
    shows = json.load(io.open(SHOWS, encoding="utf-8"))
    shows = shows.get("shows") or shows

    # 本批範圍 = 帳本提過的組,加上目錄裡所有中國原創組
    live_cn = {s["group"] for s in shows if s.get("tag") == "中國原創"}
    live_any = {s["group"] for s in shows}
    bad = 0

    missing = sorted(live_cn - set(entries))
    if missing:
        bad += len(missing)
        print("❌ 目錄有、帳本沒有(漏建帳)%d 組:" % len(missing))
        for g in missing:
            print("   ", g)
    else:
        print("○  目錄的中國原創組全部有帳本條目(%d 組)" % len(live_cn))

    orphan = [g for g in sorted(set(entries) - live_any)]
    if orphan:
        print("\n帳本有、目錄沒有 %d 組(每一組都必須有 catalog_status 說明原因):" % len(orphan))
        for g in orphan:
            why = entries[g].get("catalog_status")
            ok = bool(why)
            if not ok:
                bad += 1
            print("   %s %-24s %s" % ("○ " if ok else "❌", g[:24],
                                      (why or "🚨 沒有 catalog_status —— 這通常代表【鍵打錯】或【重複條目】")[:90]))

    # status ↔ official_plot 自洽
    print("")
    incon = []
    for g, e in entries.items():
        has = bool((e.get("official_plot") or "").strip())
        st = e.get("status")
        if has and st == "partial":
            incon.append((g, "有官方劇情卻標 partial"))
        if not has and st == "official_collected":
            incon.append((g, "沒有官方劇情卻標 official_collected"))
    if incon:
        bad += len(incon)
        print("❌ status 與 official_plot 不自洽 %d 組:" % len(incon))
        for g, why in incon:
            print("   %-24s %s" % (g[:24], why))
    else:
        print("○  status 與 official_plot 全部自洽")

    need = [g for g in entries if not entries[g].get("catalog_status", "").startswith("⛔")]
    print("\n帳本 %d 組 | 需要簡介 %d 組 | 已下架不需生成 %d 組"
          % (len(entries), len(need), len(entries) - len(need)))
    print("\n%s" % ("✅ 對帳無誤" if bad == 0 else "🚨 有 %d 個問題要處理" % bad))
    return 1 if bad else 0


raise SystemExit(main())
