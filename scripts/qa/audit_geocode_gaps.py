# -*- coding: utf-8 -*-
"""地理編碼缺口稽核 —— 把「靜默丟棄」變成看得見的數字。

為什麼需要這支
--------------
9 支爬蟲用 `scrapers/geocode.py`,但**只有 `interpark.py` 會把自己丟掉的東西
印出來**(`meta.dropped_no_coords`),其餘 8 支(atg / atrapalo / barcelona /
broadway_tours / intl / italy / madrid / westend)定不出座標就靜默跳過。
結果是:場次少了,但資料照樣產出、CI 照樣全綠、筆數也不會暴跌 —— 從外面完全看不出來。
2026-09-02 追一檔漏抓的韓國戲時才發現 interpark 一次丟掉 82 檔,其他 8 支丟多少沒人知道。

判準:為什麼要看 last_seen
-------------------------
快取裡的「查不到」混了兩種完全不同的東西:
  (a) **真缺口** —— 這一輪真的被查過、真的定不出座標 → 有場次正在被丟掉
  (b) **死鍵**   —— 舊格式留下的 key,場館早就有座標了或已下檔 → 無害
2026-09-02 實測:110 筆「查不到」裡有 **75 筆是 (b)**。
只數快取裡的 None 會把死鍵當缺口,得到一個嚇人但沒意義的數字 ——
所以 `geocode.py` 會在每次查詢時記 `last_seen`,這支只把【最近查過的】算成缺口。

⚠️ `last_seen` 是 2026-09-02 才加的,在那之前的舊項目沒有這個欄位。
   沒有 last_seen 的一律歸為「狀態未知」,不計入缺口也不計入死鍵 ——
   等各爬蟲各跑過一輪後就會自動分類完成,不要在那之前拿這裡的數字下結論。

用法:
  python scripts/qa/audit_geocode_gaps.py          # 報告
  python scripts/qa/audit_geocode_gaps.py --prune  # 順便刪掉超過 90 天沒被查過的死鍵
"""
import datetime as dt
import io
import json
import os
import sys
from collections import Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

CACHE = os.path.join("data", "venues.json")
FRESH_DAYS = 14      # 這麼多天內被查過 = 現行使用中
STALE_DAYS = 90      # 這麼久沒被查過 = 可以清掉


def country_of(query):
    """從查詢字串尾端取國家。geocode 的 query 慣例是「場館, 城市, 國家」。"""
    return (str(query or "").rsplit(",", 1)[-1]).strip() or "(不明)"


def main():
    if not os.path.exists(CACHE):
        print("找不到 %s" % CACHE)
        return 0
    cache = json.load(io.open(CACHE, encoding="utf-8"))
    today = dt.date.today()

    live, stale, unknown = [], [], []
    for slug, v in cache.items():
        if v.get("lat") is not None:
            continue                      # 有座標,不是缺口
        ls = v.get("last_seen")
        if not ls:
            unknown.append((slug, v))
            continue
        try:
            age = (today - dt.date.fromisoformat(ls)).days
        except ValueError:
            unknown.append((slug, v))
            continue
        (live if age <= FRESH_DAYS else stale if age >= STALE_DAYS else unknown).append((slug, v))

    total = len(cache)
    placed = sum(1 for v in cache.values() if v.get("lat") is not None)
    print("地理編碼快取:%d 筆,其中有座標 %d 筆(%.1f%%)"
          % (total, placed, 100.0 * placed / total if total else 0))
    print()

    print("【真缺口】最近 %d 天內被查過、仍定不出座標:%d 個場館" % (FRESH_DAYS, len(live)))
    if live:
        print("  → 這些場館的場次正在被靜默丟棄。按國家:")
        for c, n in Counter(country_of(v.get("query")) for _, v in live).most_common():
            print("     %-24s %d" % (c, n))
        print("  → 逐筆(最多 20 筆):")
        for _, v in live[:20]:
            src = v.get("src") or "?"
            print("     [%-12s] %s" % (src, str(v.get("query"))[:70]))
    else:
        print("  ✓ 沒有")
    print()

    print("【狀態未知】沒有 last_seen 或介於 %d~%d 天:%d 筆" % (FRESH_DAYS, STALE_DAYS, len(unknown)))
    print("  (last_seen 是 2026-09-02 才加的;各爬蟲各跑過一輪後這個數字會自動歸位)")
    print("【死鍵】超過 %d 天沒被查過:%d 筆(可清理,無害)" % (STALE_DAYS, len(stale)))

    if "--prune" in sys.argv and stale:
        for slug, _ in stale:
            cache.pop(slug, None)
        json.dump(cache, io.open(CACHE, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print("  → 已清掉 %d 筆死鍵,快取剩 %d 筆" % (len(stale), len(cache)))

    # 資訊性稽核,不擋 CI:一個真的查不到的偏遠場館不該讓整個 build 變紅。
    return 0


sys.exit(main())
