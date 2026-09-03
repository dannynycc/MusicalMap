# -*- coding: utf-8 -*-
"""中國原創 82 組:抓官方詳情(文字 + 詳情長圖)。

各來源的詳情放在哪裡(2026-09-04 全部實測完,前兩條原本寫錯,已更正):
  damai        —— 頁面內嵌 JSON 的 itemExtendInfo.itemExtend 是 URL-encoded HTML。
                  劇情【大多在長圖裡】,但至少 16 組在文字裡(有些連「劇情簡介」標題都沒有),
                  兩邊都要看。
  shcstheatre  —— ❌ 不是「一般 HTML 抓得到」:節目內容是【非同步塞進 DOM】的,
                  純 HTTP 只會拿到全站共用版面(《宝玉》與《边城》曾抓到一字不差的 4781 字
                  就是這個)。要打後端 /webapi.ashx?op=GettblprogramCache(見 fetch_shcs.py)。
  polyt        —— ❌ 不是「抓不到」:有公開 JSON API。
                  /good/search-products-data 找 productId,再打 /good/project/detail/{id}。
                  ⚠ /good/product-info/{id} 是陷阱,它會【忽略 id】固定回傳同一筆。
  juooo        —— 純前端渲染,HTML 抓不到,要 Playwright(見 fetch_js.py)。

🚨 長圖必須【本人逐張看】,agent 與純文字管線都讀不到。這支只負責把圖抓下來。

用法: python scratchpad/cn82/harvest.py
輸出: scratchpad/cn82/raw.json         每組的來源、文字、圖片清單
      scratchpad/cn82/img/<group>_N.<ext>
"""
import io
import json
import os
import re
import sys
import time
from urllib.parse import unquote

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from curl_cffi import requests as rq

BASE = "scratchpad/cn82"
IMG = BASE + "/img"
COV = ("C:/Users/Home/AppData/Local/Temp/claude/C--Users-Home/"
       "ed43210e-53c7-4cd6-bfb3-921d9302504e/scratchpad/cov_0903.json")


def safe(name):
    return re.sub(r"[^0-9A-Za-z\u4e00-\u9fff]+", "_", name)[:40]


def damai(url):
    """回傳 (文字, 圖片URL清單)。劇情在圖裡,文字通常只有購票須知。"""
    r = rq.get(url, impersonate="chrome", timeout=30)
    text, imgs = "", []
    for b in re.findall(r'(\{"[^\n]{200,}\})', r.text):
        try:
            d = json.loads(b)
        except Exception:
            continue
        ie = (d.get("itemExtendInfo") or {}).get("itemExtend")
        if ie:
            raw = unquote(ie)
            imgs = re.findall(r'src="([^"]+)"', raw)
            text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", raw)).strip()
            break
    return text, imgs


def generic(url):
    r = rq.get(url, impersonate="chrome", timeout=30)
    h = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", r.text, flags=re.S | re.I)
    ps = [re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", p)).strip()
          for p in re.findall(r"<p[^>]*>(.*?)</p>", h, re.S)]
    ps = [p for p in ps if len(p) > 40]
    imgs = re.findall(r'src="(https?://[^"]+\.(?:jpg|jpeg|png))"', r.text, re.I)
    return "\n".join(ps[:8]), imgs[:8]


def main():
    os.makedirs(IMG, exist_ok=True)
    cov = json.load(io.open(COV, encoding="utf-8"))
    cn = {r["group"] for r in cov if r["tag"] == "中國原創"}
    shows = json.load(io.open("data/shows.json", encoding="utf-8"))
    shows = shows.get("shows") or shows
    # 🚨 每組要挑【有詳情頁】的那一筆,不能無腦取第一筆:
    #    《男孩、鼹鼠、狐狸和马》第一筆(珠海場)的 ticket_url 是大麥【搜尋頁】,
    #    整組因此抓不到任何素材 —— 但同組廈門場其實有正常的 detail.damai.cn 詳情頁。
    picked, best = [], {}
    for s in shows:
        g = s.get("group")
        if g not in cn:
            continue
        u = s.get("ticket_url") or ""
        rank = 0 if "detail.damai.cn" in u else (1 if "search." not in u else 2)
        if g not in best or rank < best[g][0]:
            best[g] = (rank, s)
    picked = [v[1] for v in best.values()]
    print("目標 %d 組" % len(picked))

    out = {}
    for i, s in enumerate(picked, 1):
        g = s["group"]
        url = s.get("ticket_url") or ""
        src = s.get("source")
        rec = {"group": g, "title": s.get("title"), "city": s.get("city"),
               "source": src, "url": url, "text": "", "imgs": [], "files": [], "err": ""}
        try:
            if "damai" in (url or "") or src == "damai":
                rec["text"], rec["imgs"] = damai(url)
            else:
                rec["text"], rec["imgs"] = generic(url)
            # 🚨 這裡曾經寫 rec["imgs"][:6],造成 35/40 組靜默漏抓共 167 張圖
            #    (《冈格尼尔》前 6 張全是卡司、劇情在第 7 張;《时光代理人》共 28 張)。
            #    截斷不報錯、log 印「圖6」看起來完全正常,是最難發現的一種漏抓。
            #    現在【全部下載】;要限量的話請同時把來源總數印出來對照。
            for j, u in enumerate(rec["imgs"]):
                if u.startswith("//"):
                    u = "https:" + u
                try:
                    ir = rq.get(u, impersonate="chrome", timeout=40)
                    if not ir.headers.get("content-type", "").startswith("image/"):
                        continue
                    ext = ".png" if "png" in ir.headers["content-type"] else ".jpg"
                    p = "%s/%s_%d%s" % (IMG, safe(g), j, ext)
                    open(p, "wb").write(ir.content)
                    rec["files"].append({"path": p, "bytes": len(ir.content), "url": u})
                except Exception as e:
                    rec["err"] += "img%d:%s; " % (j, str(e)[:40])
        except Exception as e:
            rec["err"] = str(e)[:120]
        out[g] = rec
        print("[%2d/%d] %-24s %-12s 文字%5d 圖%d %s" %
              (i, len(picked), str(s.get("title"))[:22], src, len(rec["text"]),
               len(rec["files"]), rec["err"][:40]))
        time.sleep(0.8)

    json.dump(out, io.open(BASE + "/raw.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    ok = len([1 for v in out.values() if v["files"] or len(v["text"]) > 200])
    print("\n有官方素材(圖或長文)的:%d/%d" % (ok, len(out)))
    return 0


raise SystemExit(main())
