# -*- coding: utf-8 -*-
"""把 syn_identity.json 裡每一齣的官方詳情長圖抓下來、切成我讀得動的片段。

🚨 為什麼一定要做這步:61 齣裡只有 1 齣的 contentHtml 有文字,
其餘 60 齣的官方公演介紹【整段是圖】。純文字來源(新聞/維基/售票頁文字/agent)
結構上就拿不到官方劇情大綱 —— 這正是「本人親做」不可省的部分。

圖片網址取自 summary 的 displayTemplate/contentHtml,不用猜 -NN.jpg。
這支【只負責下載與切片】,判讀一律是我本人用 Read 逐張看。
"""
import io
import json
import os
import sys
import urllib.request

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/128.0",
      "Referer": "https://tickets.interpark.com/"}
OUT = "scratchpad/kr/detail_img"
SEG = 1600          # 每片高度(縮到寬 900 之後)


def fetch(url):
    try:
        return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40).read()
    except Exception:                                        # noqa: BLE001
        return None


def main():
    from PIL import Image
    Image.MAX_IMAGE_PIXELS = None
    os.makedirs(OUT, exist_ok=True)
    rows = json.load(io.open("scratchpad/kr/syn_identity.json", encoding="utf-8"))
    only = sys.argv[1:] or None
    idx = {}
    for r in rows:
        code = r["code"]
        if only and code not in only:
            continue
        raw = "%s/%s_raw" % (OUT, code)
        os.makedirs(raw, exist_ok=True)
        tiles = []
        for j, u in enumerate(r.get("imgs") or []):
            d = fetch(u)
            if not d or len(d) < 8000:
                continue
            p = "%s/%02d.img" % (raw, j)
            io.open(p, "wb").write(d)
            try:
                tiles.append(Image.open(p).convert("RGB"))
            except Exception:                                # noqa: BLE001
                pass
        if not tiles:
            print("%s  ⚠ 無圖" % code)
            idx[code] = []
            continue
        w = min(900, max(t.size[0] for t in tiles))
        tiles = [t.resize((w, max(1, int(t.size[1] * w / t.size[0])))) for t in tiles]
        H = sum(t.size[1] for t in tiles)
        canvas = Image.new("RGB", (w, H), "white")
        y = 0
        for t in tiles:
            canvas.paste(t, (0, y))
            y += t.size[1]
        made = []
        for i in range(0, H, SEG):
            p = "%s/%s_%02d.jpg" % (OUT, code, i // SEG)
            canvas.crop((0, i, w, min(i + SEG, H))).save(p, quality=72)
            made.append(p)
        idx[code] = made
        print("%s  %d 張圖 → %dx%d → %d 片" % (code, len(tiles), w, H, len(made)))
    json.dump(idx, io.open("%s/index.json" % OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("完成,index → %s/index.json" % OUT)
    return 0


raise SystemExit(main())
