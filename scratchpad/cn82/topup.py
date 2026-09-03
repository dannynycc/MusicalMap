# -*- coding: utf-8 -*-
"""補抓 harvest.py 被 [:6] 截掉的詳情長圖。

🚨 這支存在的原因(踩坑紀錄):harvest.py 每組只下載前 6 張圖(`rec["imgs"][:6]`),
   而《冈格尼尔》官方詳情有 7 張 —— 前 6 張全是卡司陣容,劇情簡介在【第 7 張】。
   截斷不會報錯,log 印「圖6」看起來完全正常,是【靜默漏抓】。
   所以不能只補這一組,必須把所有 damai 組回掃一次(同症狀全庫掃描)。

用法: python scratchpad/cn82/topup.py [--dry]
輸出: 補下載到 scratchpad/cn82/img/,並更新 raw.json 的 imgs/files
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
DRY = "--dry" in sys.argv


def safe(name):
    return re.sub(r"[^0-9A-Za-z一-鿿]+", "_", name)[:40]


def damai_imgs(url):
    r = rq.get(url, impersonate="chrome", timeout=30)
    for b in re.findall(r'(\{"[^\n]{200,}\})', r.text):
        try:
            d = json.loads(b)
        except Exception:
            continue
        ie = (d.get("itemExtendInfo") or {}).get("itemExtend")
        if ie:
            return re.findall(r'src="([^"]+)"', unquote(ie))
    return []


def main():
    raw = json.load(io.open(BASE + "/raw.json", encoding="utf-8"))
    # 🚨 第二輪擴大範圍。第一輪只掃「已下載滿 6 張」的組,背後假設是「不滿 6 張 = 來源就只有這麼多」。
    #    那個假設沒驗過:圖片數少也可能是【下載失敗】,一樣是靜默漏抓。而且有一批 source 欄寫著
    #    polyt.cn/juooo 的組,ticket_url 其實是 damai 詳情頁,第一輪的 source == "damai" 條件把它們全濾掉了。
    #    改成:只要 URL 是 damai 詳情頁就拿來源總數對一次,有幾張少幾張一律補。
    todo = [(g, v) for g, v in raw.items()
            if "detail.damai.cn" in (v.get("url") or "")]
    print("要回掃的 damai 詳情頁:%d 組\n" % len(todo))
    more = 0
    for i, (g, v) in enumerate(todo, 1):
        try:
            imgs = damai_imgs(v["url"])
        except Exception as e:
            print("[%2d] %-24s ✗ %s" % (i, g[:24], str(e)[:50]))
            continue
        have = len(v.get("files") or [])
        extra = imgs[have:]
        if not extra:
            print("[%2d] %-24s 共 %d 張,已齊" % (i, g[:24], len(imgs)))
            time.sleep(0.6)
            continue
        more += 1
        print("[%2d] %-24s 🚨 共 %d 張,手上 %d,漏 %d" % (i, g[:24], len(imgs), have, len(extra)))
        if DRY:
            time.sleep(0.6)
            continue
        v["imgs"] = imgs
        for j, u in enumerate(extra, start=have):
            if u.startswith("//"):
                u = "https:" + u
            try:
                ir = rq.get(u, impersonate="chrome", timeout=40)
                ct = ir.headers.get("content-type", "")
                if not ct.startswith("image/"):
                    continue
                ext = ".png" if "png" in ct else ".jpg"
                p = "%s/%s_%d%s" % (IMG, safe(g), j, ext)
                open(p, "wb").write(ir.content)
                v["files"].append({"path": p, "bytes": len(ir.content), "url": u})
                print("       + %s (%d KB)" % (os.path.basename(p), len(ir.content) // 1024))
            except Exception as e:
                print("       ✗ img%d %s" % (j, str(e)[:40]))
        time.sleep(0.6)
    if not DRY:
        json.dump(raw, io.open(BASE + "/raw.json", "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
    print("\n被截斷過的組:%d / %d" % (more, len(todo)))
    return 0


raise SystemExit(main())
