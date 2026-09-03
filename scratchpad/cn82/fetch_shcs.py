# -*- coding: utf-8 -*-
"""上海文化廣場(shcstheatre.com)節目頁:等 JS 把節目內容塞進 DOM 之後再取。

🚨 為什麼要單獨寫:這個站的 HTML 骨架是全站共用的,節目內容由 /webapi.ashx?op=Gettblprogram
   非同步塞入。用 curl 或「載入後等 3.5 秒」都只會拿到共用外殼 —— 這正是先前《宝玉》與《边城》
   兩組抓到【一字不差的 4781 字】的原因(抓到的是同一段站台版面,不是節目簡介)。
   這裡改成【等節目標題真的出現在頁面上】才取文字。

用法: python scratchpad/cn82/fetch_shcs.py <program_id> <group> <期待出現的關鍵字>
輸出: scratchpad/cn82/js/<safe(group)>.json
"""
import io
import json
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from playwright.sync_api import sync_playwright

BASE = "scratchpad/cn82"
OUT = BASE + "/js"


def safe(name):
    return re.sub(r"[^0-9A-Za-z一-鿿]+", "_", name)[:40]


def main():
    pid, group, key = sys.argv[1], sys.argv[2], sys.argv[3]
    url = ("https://www.shcstheatre.com/Program/ProgramDetails.aspx?program_id=%s" % pid)
    os.makedirs(OUT, exist_ok=True)
    with sync_playwright() as pw:
        br = pw.chromium.launch(channel="chrome", headless=True)
        ctx = br.new_context(locale="zh-CN", viewport={"width": 1400, "height": 1200})
        page = ctx.new_page()
        rec = {"group": group, "url": url, "text": "", "imgs": [], "err": ""}
        try:
            page.goto(url, wait_until="networkidle", timeout=60000)
            # 🚨 等【節目自己的關鍵字】出現,而不是等固定秒數
            page.wait_for_function(
                "k => document.body && document.body.innerText.includes(k)",
                arg=key, timeout=30000)
            page.wait_for_timeout(1500)
            rec["text"] = page.evaluate("() => document.body.innerText")
            rec["imgs"] = page.evaluate(
                "() => Array.from(document.images).map(i => i.currentSrc || i.src)"
                ".filter(s => s && s.startsWith('http'))")
        except Exception as e:
            rec["err"] = str(e)[:200]
            try:
                rec["text"] = page.evaluate("() => document.body.innerText")
            except Exception:
                pass
        finally:
            page.close()
        ctx.close()
        br.close()
    json.dump(rec, io.open("%s/%s.json" % (OUT, safe(group)), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("%s 文字%d 圖%d %s" % (group, len(rec["text"]), len(rec["imgs"]), rec["err"][:80]))
    return 0


raise SystemExit(main())
