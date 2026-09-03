# -*- coding: utf-8 -*-
"""重建 img_meta.json —— zoom.py / sheet.py 的圖片索引。

🚨 這是【衍生檔】:raw.json 一有變動(例如 topup.py 補下 167 張圖)就必須重跑,
   否則 zoom.py 會安靜地只看得到舊的 6 張,補下來的圖形同不存在,而且不會報錯。

排序:長寬比由高到低(長圖=劇情/角色頁通常最長,排前面好定位)。
用法: python scratchpad/cn82/mk_meta.py
"""
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from PIL import Image

BASE = "scratchpad/cn82"


def main():
    raw = json.load(io.open(BASE + "/raw.json", encoding="utf-8"))
    meta, n = {}, 0
    for g, v in raw.items():
        rows = []
        for f in (v.get("files") or []):
            p = f["path"]
            if not os.path.exists(p):
                continue
            try:
                w, h = Image.open(p).size
            except Exception:
                continue
            rows.append({"path": p, "w": w, "h": h, "ratio": h / float(w)})
        rows.sort(key=lambda r: -r["ratio"])
        if rows:
            meta[g] = rows
            n += len(rows)
    json.dump(meta, io.open(BASE + "/img_meta.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("img_meta.json:%d 組 / %d 張" % (len(meta), n))
    return 0


raise SystemExit(main())
