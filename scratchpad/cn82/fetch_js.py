# -*- coding: utf-8 -*-
"""用 Playwright 取【JS 渲染】的售票頁內容,補 harvest.py(純 HTTP)拿不到的組。

適用:
  juooo.com          —— 純前端渲染,HTML 抓不到任何內容
  search.damai.cn    —— 搜尋頁,要先找到詳情頁 id 才有素材
  shcstheatre.com    —— HTML 抓得到,但 generic() 抓到的是【全站共用版面】
                        (宝玉 與 边城 兩組文字一字不差 4781 字 = 抓到同一段 chrome),
                        必須取渲染後的節點文字才拿得到真正的簡介。

🚨 開分頁一定 try/finally close:CDP 分頁洩漏過一次,下次連線直接卡死。
用法: python scratchpad/cn82/fetch_js.py            (跑全部待補組)
      python scratchpad/cn82/fetch_js.py <group>    (只跑一組)
輸出: scratchpad/cn82/js/<safe(group)>.json  {url, title, text, imgs, links}
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


def targets():
    raw = json.load(io.open(BASE + "/raw.json", encoding="utf-8"))
    led = json.load(io.open(BASE + "/ledger.json", encoding="utf-8"))
    done = {k for k in led if not k.startswith("_")}
    out = []
    for g, v in raw.items():
        if g in done:
            continue
        u = v.get("url") or ""
        if "detail.damai.cn" in u:
            continue          # 這些走 topup.py,不需要瀏覽器
        out.append((g, u))
    return out


def grab(page, url):
    page.goto(url, wait_until="domcontentloaded", timeout=45000)
    page.wait_for_timeout(3500)
    try:
        page.mouse.wheel(0, 4000)
        page.wait_for_timeout(1200)
        page.mouse.wheel(0, 6000)
        page.wait_for_timeout(1200)
    except Exception:
        pass
    txt = page.evaluate("() => document.body ? document.body.innerText : ''")
    imgs = page.evaluate(
        "() => Array.from(document.images).map(i => i.currentSrc || i.src)"
        ".filter(s => s && s.startsWith('http'))")
    links = page.evaluate(
        "() => Array.from(document.querySelectorAll('a[href]')).map(a => a.href)"
        ".filter(h => /item\.htm|ticket\/|program_id/.test(h))")
    return txt, imgs, links


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    todo = [t for t in targets() if (only is None or t[0] == only)]
    if not todo:
        print("沒有待補組")
        return 1
    os.makedirs(OUT, exist_ok=True)
    print("待補 %d 組" % len(todo))
    with sync_playwright() as pw:
        br = pw.chromium.launch(channel="chrome", headless=True)
        ctx = br.new_context(
            locale="zh-CN",
            user_agent=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                        "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"),
            viewport={"width": 1400, "height": 1000})
        for i, (g, url) in enumerate(todo, 1):
            page = ctx.new_page()
            rec = {"group": g, "url": url, "text": "", "imgs": [], "links": [], "err": ""}
            try:
                rec["text"], rec["imgs"], rec["links"] = grab(page, url)
            except Exception as e:
                rec["err"] = str(e)[:160]
            finally:
                page.close()          # 🚨 洩漏分頁會讓下次 CDP 連線卡死
            json.dump(rec, io.open("%s/%s.json" % (OUT, safe(g)), "w", encoding="utf-8"),
                      ensure_ascii=False, indent=1)
            print("[%2d/%d] %-22s 文字%5d 圖%3d 連結%2d %s" %
                  (i, len(todo), g[:22], len(rec["text"]), len(rec["imgs"]),
                   len(rec["links"]), rec["err"][:50]))
        ctx.close()
        br.close()
    return 0


raise SystemExit(main())
