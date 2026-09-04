# -*- coding: utf-8 -*-
"""拿劇名去保利票務找【另一個官方來源】的劇目介紹。

用途:大麥詳情頁沒有劇情簡介的組(10 組),很多同時在保利院線巡演,
     而保利的後端有完整 projectDesp。這是【另一個官方售票來源】,不是二手轉述。

🚨 端點陷阱:/good/product-info/{id} 會【忽略 id】固定回傳同一筆(瀋陽的親子劇),
   正確的是 /good/project/detail/{productId}。這是把 H5 的 JS bundle 裡所有
   /good/... 字串掃出來才找到的。

用法: python scratchpad/cn82/poly_lookup.py
輸出: scratchpad/cn82/poly_found.json
"""
import gzip
import html
import io
import json
import re
import sys
import time
import urllib.request

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

BASE = "https://weixin.polyt.cn/platform-backend"
UA = ("Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 "
      "(KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0")
HDR = {"User-Agent": UA, "Accept-Encoding": "gzip", "Channel": "theatre_wx",
       "City-Code": "", "Content-Type": "application/json"}


def req(path, data=None):
    r = urllib.request.Request(BASE + path, headers=HDR,
                               data=json.dumps(data).encode() if data is not None else None)
    resp = urllib.request.urlopen(r, timeout=30)
    raw = resp.read()
    if resp.headers.get("Content-Encoding") == "gzip":
        raw = gzip.decompress(raw)
    return json.loads(raw.decode("utf-8", "ignore"))


def clean(s):
    s = re.sub(r"<br\s*/?>", "\n", s or "")
    s = re.sub(r"</(p|div)>", "\n", s)
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s).replace(" ", " ")
    return re.sub(r"\n{3,}", "\n\n", re.sub(r"[ \t]+", " ", s)).strip()


def main():
    led = json.load(io.open("scratchpad/cn82/ledger.json", encoding="utf-8"))
    ident = json.load(io.open("scratchpad/cn82/identity.json", encoding="utf-8"))
    todo = [g for g in ident if not (led[g].get("official_plot") or "").strip()]
    out = {}
    for g in todo:
        kw = re.sub(r"\s*[A-Za-z].*$", "", led[g].get("title") or g).strip() or g
        kw = kw.replace("《", "").replace("》", "")
        rec = {"group": g, "keyword": kw, "hits": []}
        try:
            j = req("/good/search-products-data", {"keyword": kw, "page": 1, "size": 20})
            recs = ((j.get("data") or {}).get("records")) or []
        except Exception as e:
            rec["err"] = str(e)[:80]
            recs = []
        seen = set()
        for r in recs:
            pid = r.get("productId")
            if not pid or pid in seen:
                continue
            seen.add(pid)
            if r.get("categoryName") not in ("音乐剧", "戏剧", "儿童剧"):
                continue
            try:
                d = (req("/good/project/detail/%s" % pid) or {}).get("data") or {}
            except Exception:
                continue
            desp = clean(d.get("projectDesp"))
            rec["hits"].append({"productId": pid, "name": d.get("productName"),
                                "city": d.get("cityName"), "cat": r.get("categoryName"),
                                "desp_len": len(desp), "desp": desp})
            time.sleep(0.4)
        out[g] = rec
        best = max((h["desp_len"] for h in rec["hits"]), default=0)
        print("%-16s kw=%-12s 命中 %d 筆,最長介紹 %d 字" % (g[:16], kw[:12], len(rec["hits"]), best))
        time.sleep(0.5)
    json.dump(out, io.open("scratchpad/cn82/poly_found.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return 0


raise SystemExit(main())
