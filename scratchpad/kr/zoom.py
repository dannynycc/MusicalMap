# -*- coding: utf-8 -*-
"""把官方詳情長圖的指定區塊放大後另存,供我逐字讀。

為什麼需要:有些檔的整份公演介紹是【一張小圖】(如 750x1060),
直接讀會因為字太小而讀不準。切區塊 + LANCZOS 放大後就讀得到。
只做裁切與放大,不做任何判讀。

用法: python scratchpad/kr/zoom.py <code> <x0> <y0> <x1> <y1> [scale] [tag]
"""
import io
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from PIL import Image                                        # noqa: E402
Image.MAX_IMAGE_PIXELS = None

code = sys.argv[1]
x0, y0, x1, y1 = (int(v) for v in sys.argv[2:6])
scale = float(sys.argv[6]) if len(sys.argv) > 6 else 4.0
tag = sys.argv[7] if len(sys.argv) > 7 else "zoom"
raw = "scratchpad/kr/detail_img/%s_raw" % code
files = sorted(f for f in os.listdir(raw))
im = Image.open(os.path.join(raw, files[0])).convert("RGB")
if len(files) > 1:                                           # 多張時上下接起來再切
    tiles = [Image.open(os.path.join(raw, f)).convert("RGB") for f in files]
    w = max(t.size[0] for t in tiles)
    tiles = [t.resize((w, int(t.size[1] * w / t.size[0]))) for t in tiles]
    im = Image.new("RGB", (w, sum(t.size[1] for t in tiles)), "white")
    y = 0
    for t in tiles:
        im.paste(t, (0, y)); y += t.size[1]
print("來源尺寸", im.size)
c = im.crop((x0, y0, min(x1, im.size[0]), min(y1, im.size[1])))
c = c.resize((int(c.size[0] * scale), int(c.size[1] * scale)), Image.LANCZOS)
if c.size[1] > 2000:
    c = c.resize((int(c.size[0] * 2000 / c.size[1]), 2000), Image.LANCZOS)
p = "scratchpad/kr/detail_img/%s_%s.jpg" % (code, tag)
c.save(p, quality=92)
print("→", p, c.size)
