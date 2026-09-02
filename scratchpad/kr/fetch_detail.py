# -*- coding: utf-8 -*-
"""抓 NOL 官方詳情頁,取出判斷「是不是音樂劇」需要的欄位。

詳情頁是伺服器渲染,HTML 裡內嵌完整 JSON(genreName / subGenreName / subGoodsName /
place / casting / 介紹文),所以不必開瀏覽器逐頁看。

⚠ 不要只看 genreName —— 它一律是 Musical(因為我們就是從 genreType=MUSICAL 拉的),
  等於恆真、零資訊。真正有鑑別力的是 subGoodsName、placeName、casting 有沒有人,
  以及介紹文裡的字眼。
"""
import io
import json
import re
import sys
import time
import urllib.request

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/128.0 Safari/537.36",
      "Accept-Language": "ko-KR,ko;q=0.9,en;q=0.8"}


def strip_tags(h):
    h = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", h, flags=re.S | re.I)
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", h)).strip()


def grab(url):
    h = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) \
        .read().decode("utf-8", "replace")
    out = {}
    # 內嵌 JSON 是被跳脫過的("\"key\":\"val\""),用寬鬆正則挑欄位
    for f in ("genreName", "subGenreName", "subGoodsName", "goodsName",
              "placeName", "rankingGenreName", "runningTime", "corporationName"):
        m = re.search(r'\\"%s\\":\\"(.*?)\\"' % f, h)
        if m:
            out[f] = m.group(1)
    # 卡司有沒有人 —— 有具名角色通常是戲劇作品,空的常是體驗/入場券型商品
    m = re.search(r'\\"casting\\":\[(.{0,400})', h)
    out["casting_head"] = (m.group(1)[:200] if m else "")
    # 頁面可見文字裡的 Genre / Venue / Run time 區塊
    txt = strip_tags(h)
    m = re.search(r"Genre\s+(.{0,40}?)\s+Venue\s+(.{0,60}?)\s+(Age group|Run time)", txt)
    if m:
        out["ui_genre"], out["ui_venue"] = m.group(1), m.group(2)
    out["_txtlen"] = len(txt)
    return out


def main():
    targets = json.load(io.open(sys.argv[1], encoding="utf-8"))
    res = []
    for i, t in enumerate(targets, 1):
        try:
            d = grab(t["url"])
        except Exception as e:                       # noqa: BLE001
            d = {"error": str(e)}
        d["group"] = t["group"]
        d["verdict_auto"] = t.get("verdict")
        res.append(d)
        print("%2d/%d %-34s ui_genre=%-10s venue=%-24s sub=%-18s subGoods=%s"
              % (i, len(targets), t["group"][:34], d.get("ui_genre", "?"),
                 (d.get("ui_venue") or "?")[:24], (d.get("subGenreName") or "?")[:18],
                 (d.get("subGoodsName") or "")[:26]))
        time.sleep(0.7)                              # 不要打太快
    json.dump(res, io.open("scratchpad/kr/detail.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("\n→ scratchpad/kr/detail.json")
    return 0


raise SystemExit(main())
