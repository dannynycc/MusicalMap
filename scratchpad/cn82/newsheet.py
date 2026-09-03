# -*- coding: utf-8 -*-
"""把 topup.py 補下載的圖(index>=6)跨組拼成大接觸表,快速判斷「補到的內容是什麼」。

背景:harvest.py 的 [:6] 截斷讓 35/40 組素材不完整,其中 26 組【已經進帳本】。
要判斷那些帳本是否受影響,得看補到的圖裡有沒有劇情簡介/角色卡。一組一組開太慢,
這支把補圖縮成小圖、每張 10 個併成一張,配合 stdout 的圖例即可定位。

用法: python scratchpad/cn82/newsheet.py [每張幾格=10] [格寬=280]
輸出: scratchpad/cn82/sheet/_new_<n>.jpg + stdout 圖例
"""
import io
import json
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from PIL import Image

BASE = "scratchpad/cn82"


def main():
    per = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    cw = int(sys.argv[2]) if len(sys.argv) > 2 else 280
    raw = json.load(io.open(BASE + "/raw.json", encoding="utf-8"))
    items = []
    for g, v in raw.items():
        for f in (v.get("files") or []):
            m = re.search(r"_(\d+)\.(jpg|png)$", f["path"])
            if m and int(m.group(1)) >= 6:
                items.append((g, int(m.group(1)), f["path"]))
    items.sort()
    print("補下載的圖共 %d 張,分 %d 張接觸表\n" % (items and len(items) or 0,
                                          (len(items) + per - 1) // per))
    os.makedirs(BASE + "/sheet", exist_ok=True)
    for n in range(0, len(items), per):
        chunk = items[n:n + per]
        cols = []
        for g, idx, p in chunk:
            im = Image.open(p).convert("RGB")
            h = int(im.height * cw / im.width)
            im = im.resize((cw, h), Image.LANCZOS)
            if h > 2000:
                im = im.resize((int(cw * 2000 / h), 2000), Image.LANCZOS)
            cols.append(im)
        W = sum(im.width + 8 for im in cols) + 8
        H = max(im.height for im in cols) + 8
        sheet = Image.new("RGB", (W, H), (20, 20, 20))
        x = 8
        for im in cols:
            sheet.paste(im, (x, 8))
            x += im.width + 8
        out = "%s/sheet/_new_%d.jpg" % (BASE, n // per)
        sheet.save(out, quality=86)
        print(out)
        for k, (g, idx, p) in enumerate(chunk):
            print("   格 %d = %s  第%d張" % (k, g, idx))
        print("")
    return 0


raise SystemExit(main())
