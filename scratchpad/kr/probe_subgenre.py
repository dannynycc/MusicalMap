# -*- coding: utf-8 -*-
"""問來源自己:Interpark 把每一檔歸在哪個子類。

為什麼先做這步:今天 v2.107.0 拿掉 globalType=EN 之後,韓國一次進了 69 組,
但「是不是音樂劇」一項都沒查。與其我逐檔猜,先看官方分類欄位 subGenreName ——
scraper 目前只用它擋掉 Non Verbal Performance,其餘子類是什麼從來沒看過。
(對齊 memory `feedback_use_official_source`:先問官方有沒有,別自己造輪子。)
"""
import io
import json
import sys
import urllib.parse
import urllib.request
from collections import Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

API = "https://world.nol.com/api/ent-channel-out/v1/goods/list"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) MusicalMap/0.1"


def fetch(page):
    qs = urllib.parse.urlencode({
        "goodsStatus": "Y,D", "genreType": "MUSICAL",
        "page": page, "size": 15, "includeNonPartnerGoods": "true",
    })
    req = urllib.request.Request(API + "?" + qs, headers={"User-Agent": UA})
    return json.loads(urllib.request.urlopen(req, timeout=30).read().decode("utf-8"))["data"]


def main():
    page, items, total = 1, [], None
    while page < 40:                      # 硬上限,不靠 totalPages(來源會算錯)
        d = fetch(page)
        batch = d.get("content") or []
        total = d.get("totalElements") or total
        if not batch:
            break
        items += batch
        if total and len(items) >= total:
            break
        page += 1
    print("取得 %d 檔(來源宣稱 totalElements=%s)" % (len(items), total))
    print()
    print("subGenreName 分布:")
    for k, v in Counter((it.get("subGenreName") or "(空)").strip() for it in items).most_common():
        print("   %-32s %d" % (k, v))
    print()
    print("genreName 分布:")
    for k, v in Counter((it.get("genreName") or "(空)").strip() for it in items).most_common():
        print("   %-32s %d" % (k, v))
    print()
    print("每一檔可用的欄位(第一筆):")
    print("   " + ", ".join(sorted(items[0].keys())))

    # 存【完整】原始記錄,不要只挑幾個欄位 —— 之前挑了 6 個欄位,
    # 後來想看 goodsKeyword / casting / propertyList 又得重打一次 API。
    json.dump(items, io.open("scratchpad/kr/nol_raw.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("\n原始清單(完整欄位) → scratchpad/kr/nol_raw.json")
    return 0


raise SystemExit(main())
