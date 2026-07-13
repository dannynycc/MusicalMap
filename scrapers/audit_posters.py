"""海報守門稽核(2026-07-13,「90 張換圖是一次性的,以後怎麼 gating」的答案)。

每日輕量三檢(全量版 audit_images.py 太重只手動跑):
1. 釘圖健康:works.json 所有 poster URL HEAD 驗 200+image/*——外站釘圖死了當天知道。
2. 庫存圖普查:s1.ticketm.net/dam/c/ 的 group 清單與 baseline 比對,**新出現的才警告**
   ——未來的 BOOP! 案自動浮出,不用等使用者點到。baseline=data/stock_art_baseline.json
   (審過「查無官圖」的小眾劇),新增誤報審完就補進 baseline。
3. 縮圖迴歸哨兵:已知縮圖 pattern(programinfo -NNN-NNN- 等)必須 0 張——scraper 治本
   的迴歸保險絲。
4. 抽樣尺寸檢:每日隨機 12 張非釘圖下載驗高度 ≥340px 與可解碼(種子=日期,月滾 ~360 張)
   ——未知來源的糊圖/死圖靠輪替抽樣撞。
"""
import io
import json
import random
import re
import sys
import time
import urllib.request
from datetime import date
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
DATA = Path(__file__).resolve().parent.parent / "data"
MIN_H = 340
SAMPLE = 12
THUMB_PATTERNS = [re.compile(r"programinfo\.hu/.*-\d+-\d+-\d+\.webp$")]


ROOT = DATA.parent


def is_local(u):
    return bool(u) and not u.startswith(("http://", "https://"))


def local_ok(u):
    return (ROOT / u).is_file()   # repo 自託管海報(posters/…)驗檔案存在即可


def head(u):
    req = urllib.request.Request(u, method="HEAD", headers={"User-Agent": "Mozilla/5.0"})
    return urllib.request.urlopen(req, timeout=25)


def main():
    shows = json.loads((DATA / "shows.json").read_text(encoding="utf-8"))["shows"]
    works = json.loads((DATA / "works.json").read_text(encoding="utf-8"))["works"]
    bad = []

    # 1) 釘圖健康
    pins = [(w["canonical"], w["poster"]) for w in works
            if w.get("poster") and w["poster"] != "auto"]
    for name, u in pins:
        if is_local(u):
            if not local_ok(u):
                bad.append(f"釘圖本地檔缺失: {name!r} {u}")
            continue
        try:
            r = head(u)
            ct = r.headers.get("Content-Type") or ""
            if r.status != 200 or not ct.startswith("image/"):
                bad.append(f"釘圖異常: {name!r} {r.status} {ct} {u[:70]}")
        except Exception as e:  # noqa: BLE001
            bad.append(f"釘圖死鏈: {name!r} {str(e)[:50]} {u[:70]}")
        time.sleep(0.15)

    # 2) 庫存圖普查 vs baseline
    stock_groups = sorted({s.get("group") or s["title"] for s in shows
                           if "s1.ticketm.net/dam/c/" in (s.get("image") or "")})
    bl_path = DATA / "stock_art_baseline.json"
    baseline = set(json.loads(bl_path.read_text(encoding="utf-8"))) if bl_path.exists() else set()
    for g in stock_groups:
        if g not in baseline:
            bad.append(f"新庫存圖 group: {g!r}(找官圖釘入 works,或審後補進 stock_art_baseline.json)")

    # 3) 縮圖迴歸哨兵
    for s in shows:
        u = s.get("image") or ""
        if any(p.search(u) for p in THUMB_PATTERNS):
            bad.append(f"縮圖迴歸: {s.get('title')!r} {u[:80]}")

    # 4) 抽樣尺寸/可解碼
    try:
        from PIL import Image
        pin_urls = {u for _, u in pins}
        pool = sorted({s["image"] for s in shows if s.get("image") and s["image"] not in pin_urls})
        rng = random.Random(date.today().isoformat())
        for u in rng.sample(pool, min(SAMPLE, len(pool))):
            if is_local(u):
                if not local_ok(u):
                    bad.append(f"抽樣本地檔缺失: {u}")
                continue
            try:
                req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
                raw = urllib.request.urlopen(req, timeout=25).read()
                im = Image.open(io.BytesIO(raw))
                if im.size[1] < MIN_H:
                    bad.append(f"抽樣糊圖(h={im.size[1]}<{MIN_H}): {u[:80]}")
            except Exception as e:  # noqa: BLE001
                bad.append(f"抽樣死圖: {str(e)[:50]} {u[:80]}")
            time.sleep(0.2)
    except ImportError:
        print("  (PIL 不可用,跳過抽樣尺寸檢)")

    if bad:
        print(f"海報守門 FAIL:{len(bad)} 筆")
        for b in bad:
            print("  " + b)
        sys.exit(1)
    print(f"海報守門 PASS(釘圖 {len(pins)} 健康/新庫存圖 0/縮圖迴歸 0/抽樣 {SAMPLE} 乾淨)")


if __name__ == "__main__":
    main()
