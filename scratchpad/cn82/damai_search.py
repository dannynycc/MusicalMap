# -*- coding: utf-8 -*-
"""用真 Chrome 開大麥搜尋頁,把搜尋結果的詳情頁連結撈出來。

🚨 為什麼不用 curl:大麥的 searchajax.html 對 curl_cffi 直接回傳 _____tmd_____ 反爬頁面
   (TLS/行為指紋牆),照「curl_cffi → 官方場館頁 → 真 Chrome」的升級順序,這裡要用真 Chrome。

用法: python scratchpad/cn82/damai_search.py "關鍵字" [城市]
"""
import io
import sys
import re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from urllib.parse import quote
from playwright.sync_api import sync_playwright


def main():
    kw = sys.argv[1]
    url = "https://search.damai.cn/search.htm?keyword=" + quote(kw)
    with sync_playwright() as pw:
        br = pw.chromium.launch(channel="chrome", headless=False)
        ctx = br.new_context(locale="zh-CN", viewport={"width": 1400, "height": 1000})
        page = ctx.new_page()
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(6000)
            txt = page.evaluate("() => document.body.innerText")
            links = page.evaluate(
                "() => Array.from(document.querySelectorAll('a[href]')).map(a=>a.href)"
                ".filter(h => h.includes('item.htm'))")
            m = re.search(r"共\s*(\d+)\s*个商品", txt)
            print("結果數:", m.group(1) if m else "?")
            print(txt[:900])
            for h in sorted(set(links))[:20]:
                print("   ", h)
        finally:
            page.close()
            ctx.close()
            br.close()
    return 0


raise SystemExit(main())
