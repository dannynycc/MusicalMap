# -*- coding: utf-8 -*-
"""把某一檔的官方海報與詳情長圖抓下來、切成我讀得動的片段。

🚨 為什麼需要這支(2026-09-02 使用者抓到的漏洞):
韓國音樂劇的【漢字劇名】常常只印在美術設計裡 —— 해몽가 的官方海報背景是書法
「解夢家」,主標旁也並排印著小字漢字。我和 6 個 agent 全部漏掉,因為大家都只查
文字來源(新聞/維基/售票頁文字),純文字搜尋永遠搜不到圖裡的字。
官方 SYNOPSIS 段落同樣常常整段是圖(헝키쇼 的劇情就在圖裡,agent 回報「查無」是錯的)。

這支【只負責下載與切片】,判讀一律是我本人用 Read 逐張看 —— 工具不做任何判斷。

用法: python scratchpad/kr/grab_img.py <goodsCode> [段數]
"""
import io
import os
import sys
import urllib.request

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/128.0",
      "Referer": "https://tickets.interpark.com/"}
OUT = "scratchpad/kr/img"


def fetch(url, path):
    try:
        d = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30).read()
    except Exception as e:                                   # noqa: BLE001
        return None, str(e)[:40]
    io.open(path, "wb").write(d)
    return len(d), None


def slice_img(path, stem, parts):
    from PIL import Image
    im = Image.open(path)
    w, h = im.size
    made = []
    for i in range(parts):
        a, b = h * i // parts, h * (i + 1) // parts
        c = im.crop((0, a, w, b))
        sc = min(1.0, 900.0 / c.size[0])
        c = c.resize((int(c.size[0] * sc), int(c.size[1] * sc)))
        if c.size[1] > 2100:                                 # Read 讀得動的高度上限
            c = c.crop((0, 0, c.size[0], 2100))
        p = "%s/%s_%d.jpg" % (OUT, stem, i)
        c.convert("RGB").save(p, quality=75)
        made.append(p)
    return im.size, made


def main():
    code = sys.argv[1]
    parts = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    os.makedirs(OUT, exist_ok=True)
    yy = code[:2]

    # 海報(小圖,漢字劇名常在這裡)
    pp = "%s/%s_poster.jpg" % (OUT, code)
    n, err = fetch("https://ticketimage.interpark.com/Play/image/large/%s/%s_p.gif" % (yy, code), pp)
    print("海報 %s %s" % (("OK %d bytes -> %s" % (n, pp)) if n else "FAIL " + str(err), ""))

    # 詳情長圖:編號不固定,掃一輪找出存在的
    found = []
    for i in list(range(1, 40)):
        u = "https://ticketimage.interpark.com/Play/image/etc/%s/%s-%02d.jpg" % (yy, code, i)
        p = "%s/%s-%02d.jpg" % (OUT, code, i)
        n, err = fetch(u, p)
        if n and n > 20000:
            found.append((i, n, p))
        elif os.path.exists(p):
            os.remove(p)
    print("詳情圖找到 %d 張: %s" % (len(found), [(i, "%.1fMB" % (n / 1e6)) for i, n, _ in found]))

    # 最大的那張通常是完整的公演詳情(含 SYNOPSIS)
    if found:
        i, n, p = max(found, key=lambda x: x[1])
        size, made = slice_img(p, "%s_detail" % code, parts)
        print("切最大的 %s(%s)成 %d 段:" % (p, size, len(made)))
        for m in made:
            print("   ", m)
    return 0


raise SystemExit(main())
