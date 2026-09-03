# -*- coding: utf-8 -*-
"""把一組的所有詳情長圖【縮排成一張接觸表】,用來【定位】劇情簡介在第幾張、大約幾成高度。

為什麼要這步:82 組每組 1~6 張長圖,直接一張張放大讀要 6 次 Read;先看接觸表
(每張縮到 320px 寬、並排),一次就能認出「SYNOPSIS / 剧情简介 / 角色」在哪張,
再用 zoom.py 精準放大那一段。實測可省掉七成以上的無效放大。

用法: python scratchpad/cn82/sheet.py <group> [每欄寬=320] [每欄最高=2100]
輸出: scratchpad/cn82/sheet/<group>.jpg   (欄序 = img_meta.json 的排序,即 ratio 由高到低)
"""
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from PIL import Image

BASE = "scratchpad/cn82"


def main():
    g = sys.argv[1]
    cw = int(sys.argv[2]) if len(sys.argv) > 2 else 320
    ch = int(sys.argv[3]) if len(sys.argv) > 3 else 2100
    meta = json.load(io.open("%s/img_meta.json" % BASE, encoding="utf-8"))
    if g not in meta:
        print("✗ 沒有這組:", g)
        return 1
    cols = []
    for c in meta[g]:
        im = Image.open(c["path"]).convert("RGB")
        h = int(im.height * cw / im.width)
        im = im.resize((cw, h), Image.LANCZOS)
        # 太長的圖等比壓到 ch,寧可小也要一眼看完整張的版面結構
        if h > ch:
            im = im.resize((int(cw * ch / h), ch), Image.LANCZOS)
        cols.append((os.path.basename(c["path"]), im))
    W = sum(im.width + 8 for _, im in cols) + 8
    H = max(im.height for _, im in cols) + 8
    sheet = Image.new("RGB", (W, H), (24, 24, 24))
    x = 8
    for name, im in cols:
        sheet.paste(im, (x, 8))
        x += im.width + 8
    os.makedirs(BASE + "/sheet", exist_ok=True)
    p = "%s/sheet/%s.jpg" % (BASE, g.replace("/", "_"))
    sheet.save(p, quality=88)
    print("%s → %s" % (g, p))
    for i, (name, im) in enumerate(cols):
        print("   欄 %d = %s  (原 %dx%d)" % (i, name, meta[g][i]["w"], meta[g][i]["h"]))
    return 0


raise SystemExit(main())
