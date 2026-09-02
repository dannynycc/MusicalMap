# -*- coding: utf-8 -*-
"""用 Interpark 韓國站的官方 API 驗證每一檔的【類型】與【原創/引進】。

為什麼是這支而不是先前那些
--------------------------
`world.nol.com` 的 API 只給英文子類(Creation Musicals / License / Non Verbal…),
而且我們是用 genreType=MUSICAL 去拉的 —— genreName 一律回 Musical,等於恆真、
沒有鑑別力(同 feedback_vacuous_negative_test)。

韓國站的 goods summary API 給的是韓文原始分類,兩層都有:
    genreName    뮤지컬 / 연극 / 콘서트 …   → 這到底是不是音樂劇
    genreSubName 창작뮤지컬 / 라이선스 / 내한 … → 是韓國原創還是引進授權
端點:https://api-ticketfront.interpark.com/v1/goods/{code}/summary?goodsCode={code}
(從 tickets.interpark.com 商品頁的 XHR 找到,公開、免金鑰。)

⚠ 順帶修一個今天引入的 regression:我們存的 ticket_url 指向 world.nol.com,
  但那是【國際站】,只放 globalType 非空的節目。2026-09-02 拿掉 globalType=EN
  之後多抓到的內銷場次在國際站上不存在 → 連結 404。實測 4/4 對照:
  有 globalType 全 200、沒有的全 404。內銷場次的正確網址是
  https://tickets.interpark.com/goods/{code}
"""
import io
import json
import re
import sys
import time
import urllib.error
import urllib.request

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

API = "https://api-ticketfront.interpark.com/v1/goods/%s/summary?goodsCode=%s"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/128.0 Safari/537.36",
      "Accept": "application/json",
      "Referer": "https://tickets.interpark.com/"}

FIELDS = ("goodsCode", "goodsName", "subGoodsName", "placeName",
          "genreName", "genreSubName", "viewRateName", "runningTime",
          "playStartDate", "playEndDate")


def summary(code):
    u = API % (code, code)
    with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=25) as r:
        d = json.loads(r.read().decode("utf-8"))
    return (d.get("data") or {})


def main():
    shows = json.load(io.open("data/shows.json", encoding="utf-8"))["shows"]
    codes, meta = [], {}
    for r in shows:
        if not (r.get("source") or "").startswith("world.nol"):
            continue
        c = re.sub(r"^ip-", "", r["id"])
        if c in meta:
            continue
        meta[c] = {"group": r["group"], "our_title": r.get("title"),
                   "tag": r.get("tag"), "city": r.get("city"),
                   "start": r.get("start_date"), "end": r.get("end_date")}
        codes.append(c)

    print("要查 %d 檔" % len(codes))
    out = []
    for i, c in enumerate(codes, 1):
        rec = dict(meta[c], code=c)
        try:
            d = summary(c)
            for f in FIELDS:
                rec[f] = d.get(f)
        except urllib.error.HTTPError as e:
            rec["error"] = "HTTP %s" % e.code
        except Exception as e:                       # noqa: BLE001
            rec["error"] = str(e)[:60]
        out.append(rec)
        if i % 10 == 0 or i == len(codes):
            print("  ...%d/%d" % (i, len(codes)))
        time.sleep(0.35)

    json.dump(out, io.open("scratchpad/kr/genre.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    from collections import Counter
    print()
    print("genreName(是不是音樂劇):")
    for k, v in Counter(r.get("genreName") or ("ERR:" + str(r.get("error"))) for r in out).most_common():
        print("   %-24s %d" % (k, v))
    print()
    print("genreSubName(原創 / 引進):")
    for k, v in Counter(r.get("genreSubName") or "?" for r in out).most_common():
        print("   %-24s %d" % (k, v))
    print("\n→ scratchpad/kr/genre.json")
    return 0


raise SystemExit(main())
