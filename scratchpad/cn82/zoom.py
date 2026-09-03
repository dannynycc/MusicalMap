# -*- coding: utf-8 -*-
"""把一張詳情長圖切成【等寬、可直接讀】的連續段落,不用每次猜裁切範圍。

為什麼需要:讀到第 22 組時發現裁切範圍常抓不準 ——《昨日显影》裁了三次
(第一次裁到標題、第二次寬度不夠切掉右邊、第三次才完整),因為各家排版的
文字塊寬度與位置都不一樣。與其猜,不如把整張圖切成固定高度的連續段落,
每段都放大到看得清字,照順序讀過去即可。

用法:
    python scratchpad/cn82/zoom.py <group> [段高px=1500] [起始段=0] [段數=3]
輸出: scratchpad/cn82/zoom/<group>__<n>.jpg

段高 1500 是實測值:縮放到寬 1400 後,一段約 2000px 高,中文字約 28–40px,
在 Read 工具縮到 2000px 顯示時仍可辨識。
"""
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from PIL import Image

BASE = "scratchpad/cn82"
OUT = BASE + "/zoom"
WIDTH = 1400          # 放大後的寬度


def main():
    g = sys.argv[1]
    seg_h = int(sys.argv[2]) if len(sys.argv) > 2 else 1500
    start = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    count = int(sys.argv[4]) if len(sys.argv) > 4 else 3
    which = int(sys.argv[5]) if len(sys.argv) > 5 else 0   # 第幾張圖(依 ratio 排序)

    meta = json.load(io.open("%s/img_meta.json" % BASE, encoding="utf-8"))
    if g not in meta:
        print("✗ 沒有這組:", g)
        return 1
    c = meta[g][which]
    os.makedirs(OUT, exist_ok=True)
    im = Image.open(c["path"]).convert("RGB")
    w, h = im.size
    total = (h + seg_h - 1) // seg_h
    print("%s → %s  %dx%d,每段 %dpx,共 %d 段" % (g, c["path"], w, h, seg_h, total))
    made = []
    for i in range(start, min(start + count, total)):
        y0, y1 = i * seg_h, min((i + 1) * seg_h, h)
        seg = im.crop((0, y0, w, y1))
        sh = int(seg.height * WIDTH / seg.width)
        p = "%s/%s__%d.jpg" % (OUT, g.replace("/", "_"), i)
        seg.resize((WIDTH, sh), Image.LANCZOS).save(p, quality=93)
        made.append(p)
        print("   段 %d  y=%d..%d  →  %s" % (i, y0, y1, p))
    return 0


raise SystemExit(main())
