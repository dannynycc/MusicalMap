# -*- coding: utf-8 -*-
"""把 fetch_js.py 抓到的圖片 URL 下載下來,好用 sheet.py / zoom.py 讀圖。

只收【內容圖】:過濾掉站台 logo、icon 等固定素材(路徑含 static/ 或 upload/ 的小圖),
並以 URL 去重(juooo 首圖會重複出現兩次)。

用法: python scratchpad/cn82/dl_js_imgs.py <group>
輸出: scratchpad/cn82/img/<safe(group)>_jsN.<ext>,並寫回 raw.json 的 files
"""
import io
import json
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from curl_cffi import requests as rq

BASE = "scratchpad/cn82"
IMG = BASE + "/img"
SKIP = re.compile(r"/static/|/upload/|logo|icon|qrcode", re.I)


def safe(name):
    return re.sub(r"[^0-9A-Za-z一-鿿]+", "_", name)[:40]


def main():
    g = sys.argv[1]
    p = "%s/js/%s.json" % (BASE, safe(g))
    rec = json.load(io.open(p, encoding="utf-8"))
    seen, urls = set(), []
    for u in rec["imgs"]:
        if u in seen or SKIP.search(u):
            continue
        seen.add(u)
        urls.append(u)
    os.makedirs(IMG, exist_ok=True)
    raw = json.load(io.open(BASE + "/raw.json", encoding="utf-8"))
    files = []
    for j, u in enumerate(urls):
        try:
            r = rq.get(u, impersonate="chrome", timeout=40)
            ct = r.headers.get("content-type", "")
            if not ct.startswith("image/"):
                print("   skip(非圖) %s" % u[:70])
                continue
            ext = ".png" if "png" in ct else ".jpg"
            fp = "%s/%s_js%d%s" % (IMG, safe(g), j, ext)
            open(fp, "wb").write(r.content)
            files.append({"path": fp, "bytes": len(r.content), "url": u})
            print("   %s (%d KB)" % (os.path.basename(fp), len(r.content) // 1024))
        except Exception as e:
            print("   ✗ %s %s" % (u[:60], str(e)[:40]))
    if g in raw:
        raw[g]["files"] = (raw[g].get("files") or []) + files
        raw[g]["imgs"] = urls
        json.dump(raw, io.open(BASE + "/raw.json", "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
    print("%s:下載 %d 張" % (g, len(files)))
    return 0


raise SystemExit(main())
