# -*- coding: utf-8 -*-
"""保利票務 H5 詳情頁:用真 Chrome 渲染取劇目介紹。

背景:/good/search-products-data 這支公開 API 只給列表欄位(標題/城市/場館/價格),
      productDesc 與 showDesc 都是空字串;試過 /good/product-info/{id} 會【忽略 id】
      固定回傳同一筆(瀋陽的親子互動劇),不能用。所以改渲染 H5 詳情頁。

用法: python scratchpad/cn82/poly_detail.py <productId> <group>
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
UA = ("Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 "
      "(KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0")


def safe(n):
    return re.sub(r"[^0-9A-Za-z一-鿿]+", "_", n)[:40]


def main():
    pid, group = sys.argv[1], sys.argv[2]
    os.makedirs(OUT, exist_ok=True)
    rec = {"group": group, "tried": [], "text": "", "imgs": [], "err": ""}
    tid = sys.argv[3] if len(sys.argv) > 3 else ""
    # 🚨 /product/{id} 不帶劇院參數會被導回北京保利首頁(拿到的是首頁清單,不是這齣戲)。
    #    列表 API 的 theaterId 要一起帶上。
    urls = [
        "https://weixin.polyt.cn/product/%s?theaterId=%s" % (pid, tid),
        "https://weixin.polyt.cn/product/%s?theatreId=%s" % (pid, tid),
        "https://weixin.polyt.cn/product/%s" % pid,
    ]
    with sync_playwright() as pw:
        br = pw.chromium.launch(channel="chrome", headless=True)
        ctx = br.new_context(locale="zh-CN", user_agent=UA,
                             viewport={"width": 420, "height": 900}, is_mobile=True,
                             has_touch=True)
        page = ctx.new_page()
        try:
            for u in urls:
                try:
                    page.goto(u, wait_until="domcontentloaded", timeout=45000)
                    page.wait_for_timeout(4500)
                    t = page.evaluate("() => document.body ? document.body.innerText : ''")
                    rec["tried"].append({"url": u, "len": len(t)})
                    if len(t) > len(rec["text"]):
                        rec["text"] = t
                        rec["imgs"] = page.evaluate(
                            "() => Array.from(document.images).map(i=>i.currentSrc||i.src)"
                            ".filter(s=>s&&s.startsWith('http'))")
                except Exception as e:
                    rec["tried"].append({"url": u, "err": str(e)[:80]})
        finally:
            page.close()
            ctx.close()
            br.close()
    json.dump(rec, io.open("%s/%s.json" % (OUT, safe(group)), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(group, "文字%d 圖%d" % (len(rec["text"]), len(rec["imgs"])), rec["tried"])
    return 0


raise SystemExit(main())
