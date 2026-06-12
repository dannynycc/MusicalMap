"""宝塚歌劇団 (Takarazuka Revue) — source: kageki.hankyu.co.jp

The JP revue index lists each production page (/revue/20xx/<slug>/index.html);
every page carries one or more theatre blocks with 公演期間 (run period). We
parse theatre + date range per block. Known Japanese titles are mapped to the
canonical Western musical title so e.g. エリザベート groups with Elisabeth
worldwide. Troupe og:image is used as the card image when present.

Output: data/takarazuka.json   Run: python scrapers/takarazuka.py
"""

import json
import re
import sys
import io
import time
import urllib.request
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

DATA = Path(__file__).resolve().parent.parent / "data"
BASE = "https://kageki.hankyu.co.jp"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) MusicalMap/0.1"

THEATRES = {
    "宝塚大劇場": ("宝塚大劇場", "Takarazuka (兵庫)", 34.8093, 135.3470),
    "東京宝塚劇場": ("東京宝塚劇場", "Tokyo (日比谷)", 35.6735, 139.7593),
    "御園座": ("御園座", "Nagoya", 35.1665, 136.8990),
    "博多座": ("博多座", "Fukuoka", 33.5957, 130.4137),
    "梅田芸術劇場": ("梅田芸術劇場", "Osaka", 34.7068, 135.4985),
}

# JP title → canonical Western musical title (only where it IS the same musical)
TITLES = {
    "エリザベート": "Elisabeth",
    "ロミオとジュリエット": "Roméo et Juliette",
    "ファントム": "Phantom (Maury Yeston)",
}


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    return urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "ignore")


def jp_title(html):
    m = re.search(r"<title>[^『]*『([^』]+)』", html)
    return m.group(1).strip() if m else None


def canon(title):
    for jp, en in TITLES.items():
        if title.startswith(jp):
            return en
    return title


DATE_RE = re.compile(
    r"公演期間\s*(\d{4})年(\d{1,2})月(\d{1,2})日[^0-9]{0,15}?(?:(\d{4})年)?(\d{1,2})月(\d{1,2})日")
TH_RE = re.compile(r"宝塚大劇場|東京宝塚劇場|御園座|博多座|梅田芸術劇場")


def parse_runs(html):
    """Yield (theatre_key, start_iso, end_iso) per theatre block.

    Positional parsing: each theatre-name occurrence owns only the text up to
    the NEXT theatre name, so a date range can't be attributed to the wrong
    theatre (longest names first in TH_RE avoids 東京宝塚劇場 substring issues)."""
    text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))
    hits = list(TH_RE.finditer(text))
    for i, m in enumerate(hits):
        seg_end = hits[i + 1].start() if i + 1 < len(hits) else min(len(text), m.end() + 400)
        seg = text[m.end():seg_end]
        dm = DATE_RE.search(seg[:300])
        if not dm:
            continue
        y1, mo1, d1, y2, mo2, d2 = dm.groups()
        y2 = y2 or y1
        if int(y2) < int(y1) or (y2 == y1 and int(mo2) < int(mo1)):
            y2 = str(int(y1) + 1)  # run wraps the year boundary
        yield m.group(0), f"{y1}-{int(mo1):02d}-{int(d1):02d}", f"{y2}-{int(mo2):02d}-{int(d2):02d}"


def main():
    idx = fetch(BASE + "/revue/index.html")
    pages = sorted(set(re.findall(r'href="(/revue/20\d{2}/[a-z0-9_]+/index\.html)"', idx)))
    print(f"{len(pages)} production pages")

    shows = {}
    for path in pages:
        try:
            html = fetch(BASE + path)
        except Exception as e:  # noqa: BLE001
            print(f"  [skip] {path}: {e}")
            continue
        title_jp = jp_title(html)
        if not title_jp:
            continue
        title = canon(title_jp)
        og = re.search(r'property="og:image" content="([^"]+)"', html)
        runs = list(parse_runs(html))
        for th_key, start, end in runs:
            venue, city, lat, lng = THEATRES[th_key]
            sid = "tkz-" + re.sub(r"[^a-z0-9]+", "-", f"{path.split('/')[3]}-{city}-{start}".lower()).strip("-")
            shows[sid] = {
                "id": sid,
                "title": title,
                "type": "tour",  # limited seasons → card shows the date range
                "venue": venue,
                "city": city,
                "country": "Japan",
                "lat": lat,
                "lng": lng,
                "start_date": start,
                "end_date": end,
                "ticket_url": BASE + path,
                "image": og.group(1) if og else None,
                "tour_name": f"宝塚歌劇『{title_jp}』" if title != title_jp else "宝塚歌劇",
                "verified": True,
                "source": "kageki.hankyu.co.jp",
            }
            print(f"  {title[:26]:28s} @ {venue}  {start} – {end}")
        if not runs:
            print(f"  [no dates yet] {title} ({path})")
        time.sleep(0.4)

    out = {"meta": {"source": "kageki.hankyu.co.jp", "count": len(shows)}, "shows": list(shows.values())}
    (DATA / "takarazuka.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nWrote {len(shows)} runs -> data/takarazuka.json")


if __name__ == "__main__":
    main()
