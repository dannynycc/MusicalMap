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

# Japanese performance city -> English (for 2.5D tour blocks 【横浜公演】…)
JP_CITY = {
    "東京": "Tokyo", "横浜": "Yokohama", "大阪": "Osaka", "名古屋": "Nagoya",
    "札幌": "Sapporo", "福岡": "Fukuoka", "仙台": "Sendai", "京都": "Kyoto",
    "神戸": "Kobe", "広島": "Hiroshima", "埼玉": "Saitama", "千葉": "Chiba",
    "兵庫": "Hyogo", "愛知": "Aichi", "宮城": "Miyagi", "静岡": "Shizuoka",
    "新潟": "Niigata", "金沢": "Kanazawa", "高松": "Takamatsu", "岡山": "Okayama",
    "熊本": "Kumamoto", "沖縄": "Okinawa", "長野": "Nagano", "群馬": "Gunma",
    "神奈川": "Kanagawa", "福島": "Fukushima", "栃木": "Tochigi", "茨城": "Ibaraki",
    "岐阜": "Gifu", "三重": "Mie", "滋賀": "Shiga", "山形": "Yamagata",
    "北海道": "Sapporo", "宮崎": "Miyazaki", "鹿児島": "Kagoshima", "富山": "Toyama",
}


def jp_city(s):
    """'東京凱旋', '大阪追加公演' … -> the leading prefecture/city, English."""
    s = re.sub(r"（.*|\(.*", "", s or "").strip()
    for jp in sorted(JP_CITY, key=len, reverse=True):
        if s.startswith(jp):
            return JP_CITY[jp]
    return s


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
    # poster keyed by the card's alt text (which equals the full title)
    art = {html.unescape(a).strip(): s for s, a in
           re.findall(r'card-lineup__image"\s+src="([^"]+)"[^>]*alt="([^"]+)"', h)}
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
                    "start": ds[0], "end": ds[-1], "image": art.get(title_raw),
                    "url": "https://www.toho.co.jp/stage/lineup", "source": "toho.co.jp"})
    return out, dropped


# ---------- 2.5次元 (日本2.5次元ミュージカル協会) ----------
def clean_25_title(raw):
    raw = html.unescape(raw or "")
    m = re.search(r"[『「](.+?)[』」]", raw)
    return (m.group(1) if m else re.split(r"[|｜]", raw)[0]).strip()


def scrape_j25():
    idx = get("https://www.j25musical.jp/stage/")
    ids = list(dict.fromkeys(re.findall(r"/stage/(\d+)", idx)))
    out, dropped = [], []
    for sid in ids:
        try:
            h = get(f"https://www.j25musical.jp/stage/{sid}")
        except Exception:
            continue
        og = re.search(r'property=["\']og:title["\'] content=["\']([^"\']+)', h)
        title = clean_25_title(og.group(1) if og else "")
        if not title or title in ("2.5", "SHOW SCHEDULE"):
            continue
        # the real key visual is showCtsImage.php?cid=…&no=1 in the page; og:image is
        # just the association's generic logo (img/ogimage.png) — don't use that.
        im = re.search(r"showCtsImage\.php\?cid=\d+&no=1[^\"'\) ]*", h)
        img = ("https://www.j25musical.jp/" + im.group(0)) if im else None
        sec = html.unescape(re.sub(r"<[^>]+>", " ", h))
        m = re.search(r"公演期間", sec)
        if not m:
            dropped.append(f"{title} (無公演期間)"); continue
        end_kw = re.search(r"チケット料金|チケット一般|主催|お問い合わせ", sec[m.start():])
        section = sec[m.start(): m.start() + (end_kw.start() if end_kw else 2500)]
        n = 0
        for mm in re.finditer(r"【([^】]*?)公演】(.*?)(?=【[^】]*公演】|＜[^＞]*＞|※|$)", section, re.S):
            city_jp, body = mm.group(1).strip(), mm.group(2)
            ds = jp_dates(body)
            if not ds:
                continue
            venue = re.sub(r"\d{4}年\d{1,2}月\d{1,2}日(?:\([^)]*\)|（[^）]*）)?|\d{1,2}月\d{1,2}日(?:\([^)]*\)|（[^）]*）)?|[～~・]", "", body)
            venue = re.sub(r"\s+", " ", venue).strip(" 　・")
            if not venue or len(venue) > 40:
                continue
            city = jp_city(city_jp)
            if not city.isascii():            # unmapped JP prefecture or overseas (ロンドン) — skip
                dropped.append(f"{title} (城市未對應: {city_jp})"); continue
            out.append({"title": title, "venue": venue, "city": city,
                        "start": ds[0], "end": ds[-1], "image": img,
                        "url": f"https://www.j25musical.jp/stage/{sid}", "source": "j25musical.jp"})
            n += 1
        if not n:
            dropped.append(f"{title} (無可解析場次)")
    return out, dropped


# ---------- 東急シアターオーブ (musical-dedicated venue, Shibuya) ----------
def slash_dates(text):
    """'2026/5/27(水)～6/21(日)' -> ['2026-05-27','2026-06-21'] (carry year/month)."""
    out, y, mo = [], None, None
    for t in re.finditer(r"(\d{4})/(\d{1,2})/(\d{1,2})|(\d{1,2})/(\d{1,2})", text):
        if t.group(1):
            y, mo = int(t.group(1)), int(t.group(2))
            out.append(f"{y:04d}-{mo:02d}-{int(t.group(3)):02d}")
        elif t.group(4) and y:
            mo = int(t.group(4))
            out.append(f"{y:04d}-{mo:02d}-{int(t.group(5)):02d}")
    return out


def orb_title(t):
    t = html.unescape(t or "").split("｜")[0].split("|")[0].strip()
    m = re.search(r"[「『](.+?)[」』]", t)
    if m:
        return m.group(1).strip()
    t = re.sub(r"^(?:ミュージカル|宝塚歌劇.*?公演|.*?presents)\s*", "", t, flags=re.I).strip()
    m2 = re.match(r"([A-Za-z0-9][A-Za-z0-9 '!:&.\-]+)", t)   # ASCII title, drop trailing JP reading
    return (m2.group(1).strip() if m2 else t)


def scrape_orb():
    home = get("https://theatre-orb.com/")
    slugs = list(dict.fromkeys(re.findall(r"/lineup/(26_[\w]+)/", home)))
    out, dropped = [], []
    for slug in slugs:
        try:
            h = get(f"https://theatre-orb.com/lineup/{slug}/")
        except Exception:
            continue
        og = re.search(r'og:title["\' ]+content=["\']([^"\']+)', h)
        title = orb_title(og.group(1) if og else "")
        txt = re.sub(r"<[^>]+>", " ", h)
        m = re.search(r"公演日程[\s\S]{0,15}?(\d{4}/\d{1,2}/\d{1,2})\([^)]*\)\s*[～~]\s*((?:\d{4}/)?\d{1,2}/\d{1,2})", txt)
        if not title or not m:
            dropped.append(f"orb {slug} (無題名/日程)"); continue
        ds = slash_dates(m.group(1) + " " + m.group(2))
        if not ds:
            dropped.append(f"{title} (orb 無日期)"); continue
        im = re.search(r"/data/files/[^\"'\) ]*mainvisual[^\"'\) ]*\.(?:jpg|png)", h) \
            or re.search(r"/data/files/20\d\d/[^\"'\) ]+\.(?:jpg|png)", h)
        img = ("https://theatre-orb.com" + im.group(0)) if im else None
        out.append({"title": title, "venue": "東急シアターオーブ", "city": "Tokyo",
                    "start": ds[0], "end": ds[-1], "image": img,
                    "url": f"https://theatre-orb.com/lineup/{slug}/", "source": "theatre-orb.com"})
    return out, dropped


def main():
    today = datetime.now(JST).strftime("%Y-%m-%d")
    rows, dropped = [], []
    for fn in (scrape_toho, scrape_j25, scrape_orb):
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
