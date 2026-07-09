"""Austria — Vienna's Vereinigte Bühnen Wien (musicalvienna.at), the home of the
德奧 megamusicals (Das Phantom der Oper, Maria Theresia, etc.) at the Raimund
Theater and Ronacher. The TM sweep only caught a stray Mamma Mia, missing the VBW
resident productions entirely.

Source is server-rendered: /de/spielplan lists each show as /de/spielplan/{id}/{slug};
each detail page carries og:title + og:image + German performance dates
("28. Juni 2026") + the theatre name. Run = earliest..latest dated performance.

Output: data/austria.json   Run: python scrapers/austria.py
"""

import json
import re
import sys
import io
import html
import hashlib
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
DATA = Path(__file__).resolve().parent.parent / "data"
BASE = "https://www.musicalvienna.at"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0",
      "Accept-Language": "de"}
CET = timezone(timedelta(hours=1))

# Vienna VBW houses (building-level coords).
VENUES = {
    "raimund": ("Raimund Theater", 48.196900, 16.343800),
    "ronacher": ("Ronacher", 48.207300, 16.376000),
}
DE_MONTH = {"jan": 1, "feb": 2, "mär": 3, "maer": 3, "apr": 4, "mai": 5, "jun": 6,
            "jul": 7, "aug": 8, "sep": 9, "okt": 10, "nov": 11, "dez": 12}
# Not staged book musicals: backstage tours, youth showcase/gala.
SKIP = re.compile(r"fuehrung|führung|workshop|we-are-musical|we are musical|gala", re.I)


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
        return r.read().decode("utf-8", "ignore")


def parse_dates(page):
    """All 'DD. Monat YYYY' German dates → (min, max) ISO, or (None, None)."""
    out = []
    for d, mon, y in re.findall(r"(\d{1,2})\.\s*([A-Za-zä]+)\.?\s*(20\d{2})", page):
        m = DE_MONTH.get(mon[:3].lower())
        if m:
            out.append(f"{y}-{m:02d}-{int(d):02d}")
    out.sort()
    return (out[0], out[-1]) if out else (None, None)


def run_line(page, title):
    """每頁共用的檔期列「{Raimund Theater|Ronacher} {TITLE} 10.10.2025 - 26.06.2027」=
    官方權威起迄+場館,一次拿齊。2026-07-09 修:網站改版後正文只剩新聞稿零星日期,
    舊的 parse_dates 把 Maria Theresia 判成已結束(抓到 2/20 新聞日)、美女與野獸判成
    無日期 → 整個 VBW 來源歸零(使用者抓到維也納全漏)。標題比對用「只留字母」鍵,
    容忍 – vs - 與空白差異。"""
    plain = re.sub(r"<[^>]+>", " ", page)
    tkey = re.sub(r"[^A-ZÄÖÜ]", "", (title or "").upper())[:14]
    for m in re.finditer(r"(Raimund Theater|Ronacher)\s+(.{3,90}?)\s+(\d{2})\.(\d{2})\.(20\d{2})\s*[-–]\s*(\d{2})\.(\d{2})\.(20\d{2})", plain):
        k = re.sub(r"[^A-ZÄÖÜ]", "", m.group(2).upper())[:14]
        if tkey and k and (k in tkey or tkey in k):
            start = f"{m.group(5)}-{m.group(4)}-{m.group(3)}"
            end = f"{m.group(8)}-{m.group(7)}-{m.group(6)}"
            return m.group(1), start, end
    return None, None, None


def main():
    today = datetime.now(CET).strftime("%Y-%m-%d")
    listing = get(f"{BASE}/de/spielplan")
    slugs = sorted(set(re.findall(r"/de/spielplan/\d+/[A-Za-z][\w\-]*", listing)))
    rows, dropped = [], []
    for path in slugs:
        if SKIP.search(path):
            dropped.append(f"{path} (tour/gala)"); continue
        try:
            page = get(BASE + path)
        except Exception:
            continue
        tm = re.search(r'og:title"\s+content="([^"]+)"', page)
        title = html.unescape(tm.group(1)).split("|")[0].strip() if tm else None
        if not title or SKIP.search(title):
            dropped.append(f"{path} ({title})"); continue
        # 首選:檔期列(權威場館+起迄);fallback:舊的「德文月名散抓+頁內場館出現次數」
        rv, rs, re_ = run_line(page, title)
        if rv:
            vk = "ronacher" if "ronacher" in rv.lower() else "raimund"
            start, end = rs, re_
        else:
            vk = max(VENUES, key=lambda k: len(re.findall(k, page, re.I)))
            if not re.search(vk, page, re.I):
                vk = "raimund"
            start, end = parse_dates(page)
        venue, lat, lng = VENUES[vk]
        if not start:
            dropped.append(f"{title} (no dates)"); continue
        if end and end < today:
            dropped.append(f"{title} (ended {end})"); continue
        img = re.search(r'og:image"\s+content="([^"]+)"', page)
        rows.append({
            "id": "at-" + hashlib.md5(f"vbw|{title}|{venue}".encode()).hexdigest()[:8],
            "title": title, "title_en": "",
            "venue": venue, "city": "Vienna", "country": "Austria",
            "lat": lat, "lng": lng, "start_date": start, "end_date": end,
            "image": img.group(1) if img else None,
            "ticket_url": BASE + path, "type": "resident", "verified": True,
            "tour_name": title,   # 在地製作名(DIE SCHÖNE UND DAS BIEST):卡片顯示德文版名,分類仍走 works 註冊
            "source": "musicalvienna.at",
        })

    out = {"meta": {"source": "musicalvienna.at (VBW)", "count": len(rows)}, "shows": rows}
    (DATA / "austria.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(rows)} -> data/austria.json")
    for s in rows:
        print(f"  keep: {s['title']} @ {s['venue']} {s['start_date']}~{s['end_date']}")
    for d in dropped:
        print("  drop:", d)


if __name__ == "__main__":
    main()
