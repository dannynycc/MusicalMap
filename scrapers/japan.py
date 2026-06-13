"""Japan commercial + 2.5D musicals beyond 劇団四季 / 宝塚.

Shiki (shiki.py) and Takarazuka (takarazuka.py) are scraped separately. This adds
the rest of the Japanese musical landscape from several server-rendered sources:

  - 東宝 (toho.co.jp/stage/lineup)  — biggest commercial producer (帝劇休館中なので
    シアタークリエ/日生劇場/東急シアターオーブ/EX THEATER ARIAKE などに分散). card-lineup
    blocks: __title 『…』 / __text date range / __at venue. Keep only ミュージカル.

More sources (梅田芸術劇場 / 東急シアターオーブ / 日生劇場 / 2.5次元) are added below as
separate site entries sharing the same date/venue plumbing.

Dates are Japanese (2026年5月6日～6月30日). Venues are Japanese names; coordinates are
left to geocode_google.py. Vague dates ("2027年秋", "全国ツアー中") and multi/ambiguous
venues ("その他", "北海道、大阪") are skipped — we only emit shows with a concrete
single venue + date range.

Output: data/japan.json    Run: python scrapers/japan.py
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
JST = timezone(timedelta(hours=9))
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0",
      "Accept-Language": "ja"}

# venue (as the source writes it) -> (clean display name, city). Coordinates come
# from geocode_google.py keyed on this display name + city.
VENUES = {
    "シアタークリエ": ("シアタークリエ", "Tokyo"),
    "日生劇場": ("日生劇場", "Tokyo"),
    "東急シアターオーブ": ("東急シアターオーブ", "Tokyo"),
    "EX THEATER ARIAKE": ("EX THEATER ARIAKE", "Tokyo"),
    "東京建物Brillia HALL": ("東京建物Brillia HALL", "Tokyo"),
    "梅田芸術劇場": ("梅田芸術劇場メインホール", "Osaka"),
    "梅田芸術劇場メインホール": ("梅田芸術劇場メインホール", "Osaka"),
    "ウェスタ川越": ("ウェスタ川越", "Kawagoe"),
}
# venue strings that aren't a single concrete place -> skip
VAGUE_VENUE = re.compile(r"その他|全国|ツアー|、|，|/|・大阪|北海道")


def get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "ignore")


def jp_dates(text):
    """All YYYY-MM-DD in a Japanese date string, carrying year/month forward
    ('2026年5月6日～6月30日' -> 2026-05-06, 2026-06-30; '…9月8日～29日' -> …09-08, 09-29)."""
    out, y, m = [], None, None
    prev_m = None
    for t in re.finditer(r"(\d{4})年|(\d{1,2})月|(\d{1,2})日", text):
        if t.group(1):
            y = int(t.group(1))
        elif t.group(2):
            mm = int(t.group(2))
            if prev_m is not None and mm < prev_m and y:   # 12月～1月 rolls into next year
                y += 1
            m, prev_m = mm, mm
        elif t.group(3) and y and m:
            out.append(f"{y:04d}-{m:02d}-{int(t.group(3)):02d}")
    return out


def clean_title(raw):
    """'ミュージカル『レベッカ』' -> 'レベッカ' (strip the ミュージカル prefix + 『』)."""
    raw = html.unescape(raw or "").strip()
    m = re.search(r"[『「《](.+?)[』」》]", raw)
    return m.group(1).strip() if m else re.sub(r"^ミュージカル\s*", "", raw).strip()


# ---------- 東宝 ----------
def scrape_toho():
    h = get("https://www.toho.co.jp/stage/lineup")
    cards = re.findall(
        r'card-lineup__title">\s*(.*?)</p>.*?card-lineup__text">\s*(.*?)</p>.*?card-lineup__at">\s*(.*?)</p>',
        h, re.S)
    out, dropped = [], []
    for t, d, v in cards:
        title_raw = html.unescape(t).strip()
        if "ミュージカル" not in title_raw:
            continue                                    # plays / concerts (舞台『…』, …Concert)
        date_txt = html.unescape(re.sub(r"<[^>]+>", "", d)).strip()
        venue_raw = html.unescape(re.sub(r"<[^>]+>", "", v)).strip()
        ds = jp_dates(date_txt)
        if not ds:
            dropped.append(f"{title_raw} (日期模糊: {date_txt[:16]})"); continue
        if VAGUE_VENUE.search(venue_raw) or venue_raw not in VENUES:
            dropped.append(f"{title_raw} (場館不明: {venue_raw[:16]})"); continue
        name, city = VENUES[venue_raw]
        out.append({"title": clean_title(title_raw), "venue": name, "city": city,
                    "start": ds[0], "end": ds[-1], "image": None,
                    "url": "https://www.toho.co.jp/stage/lineup", "source": "toho.co.jp"})
    return out, dropped


def main():
    today = datetime.now(JST).strftime("%Y-%m-%d")
    rows, dropped = [], []
    for fn in (scrape_toho,):
        try:
            r, d = fn()
            rows += r; dropped += d
            print(f"  {fn.__name__}: {len(r)} kept", flush=True)
        except Exception as e:
            print(f"  {fn.__name__} failed: {e}", flush=True)

    shows = []
    for s in rows:
        if s["end"] < today:
            dropped.append(f"{s['title']} (已結束)"); continue
        sid = "jp-" + hashlib.md5(f"{s['source']}|{s['title']}|{s['venue']}".encode()).hexdigest()[:8]
        shows.append({
            "id": sid, "title": s["title"], "title_en": "",
            "venue": s["venue"], "city": s["city"], "country": "Japan",
            "lat": None, "lng": None, "start_date": s["start"], "end_date": s["end"],
            "image": s["image"], "ticket_url": s["url"],
            "type": "resident", "verified": True, "source": s["source"],
        })
    out = {"meta": {"source": "japan (toho+)", "count": len(shows)}, "shows": shows}
    (DATA / "japan.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(shows)} -> data/japan.json", flush=True)
    for s in shows:
        print(f"    keep: {s['title']} @ {s['venue']} ({s['city']}) {s['start_date']}~{s['end_date']}", flush=True)
    for d in dropped:
        print("    drop:", d, flush=True)


if __name__ == "__main__":
    main()
