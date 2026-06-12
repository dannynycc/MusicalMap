"""劇団四季 (Shiki Theatre Company) — source: shiki.jp/api_stage_list

Their schedule page is JS-rendered but backed by a clean JSON API listing every
production by region with theatre + exact run dates (YYYYMMDD). We keep the
fixed-theatre productions (Tokyo/Yokohama/Maihama/Nagoya/Osaka …) and map the
Japanese titles to canonical English ones so they group/merge with the same
shows worldwide. 全国ツアー (national tour) rows have no fixed city/venue in the
API — skipped honestly rather than guessed.

NOTE: shiki.jp supersedes broadway.org's Japan data (which e.g. still placed
The Lion King at the old HARU theatre instead of 有明四季劇場); build_shows.py
drops intl.json Japan records that shiki.json also covers.

Output: data/shiki.json   Run: python scrapers/shiki.py
"""

import json
import re
import sys
import io
import urllib.request
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

DATA = Path(__file__).resolve().parent.parent / "data"
API = "https://www.shiki.jp/api_stage_list"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) MusicalMap/0.1"

# JP production name (prefix) -> canonical English title (groups worldwide)
TITLES = {
    "アナと雪の女王": "Frozen",
    "バック・トゥ・ザ・フューチャー": "Back to the Future: The Musical",
    "コーラスライン": "A Chorus Line",
    "アラジン": "Aladdin",
    "ライオンキング": "The Lion King",
    "マンマ・ミーア！": "Mamma Mia!",
    "リトルマーメイド": "The Little Mermaid",
    "オペラ座の怪人": "The Phantom of the Opera",
    "ノートルダムの鐘": "The Hunchback of Notre Dame",
    "ウィキッド": "Wicked",
    "キャッツ": "CATS",
    "王様の耳はロバの耳": "王様の耳はロバの耳 (The King's Donkey Ears)",
}

# Shiki's own (stable) theatres — landmark-level coordinates.
THEATRES = {
    "ＪＲ東日本四季劇場［春］": ("JR東日本四季劇場[春] (竹芝)", "Tokyo", 35.6546, 139.7615),
    "ＪＲ東日本四季劇場［秋］": ("JR東日本四季劇場[秋] (竹芝)", "Tokyo", 35.6552, 139.7628),
    "自由劇場": ("自由劇場 (浜松町)", "Tokyo", 35.6556, 139.7584),
    "電通四季劇場［海］": ("電通四季劇場[海] (汐留)", "Tokyo", 35.6647, 139.7611),
    "有明四季劇場": ("有明四季劇場", "Tokyo", 35.6362, 139.7920),
    "ＫＡＡＴ": ("KAAT 神奈川芸術劇場", "Yokohama", 35.4441, 139.6362),
    "舞浜アンフィシアター": ("舞浜アンフィシアター", "Maihama", 35.6267, 139.8850),
    "ＭＴＧ名古屋四季劇場": ("MTG名古屋四季劇場", "Nagoya", 35.1545, 136.8847),
    "大阪四季劇場": ("大阪四季劇場 (梅田)", "Osaka", 34.7008, 135.4938),
}


def iso(d):
    return f"{d[:4]}-{d[4:6]}-{d[6:8]}" if d and len(d) == 8 else None


def main():
    req = urllib.request.Request(API, headers={"User-Agent": UA})
    data = json.loads(urllib.request.urlopen(req, timeout=30).read().decode("utf-8"))
    regions = data if isinstance(data, list) else list(data.values())[0]

    shows, skipped = {}, 0
    for reg in regions:
        for st in reg.get("stages", []):
            theater = st.get("theater_name") or ""
            match = next((v for k, v in THEATRES.items() if theater.startswith(k)), None)
            if not match:           # 全国ツアー or unknown venue — no fixed city
                skipped += 1
                continue
            venue, city, lat, lng = match
            koen = st.get("koen_name") or ""
            title = next((en for jp, en in TITLES.items() if koen.startswith(jp)), koen)
            start, end = iso(st.get("from")), iso(st.get("to"))
            if not start:
                continue
            img = st.get("img_l") or st.get("img")
            sid = "shiki-" + re.sub(r"[^a-z0-9]+", "-",
                                    f"{title}-{city}-{start}".lower()).strip("-")
            shows[sid] = {
                "id": sid,
                "title": title,
                "type": "resident",
                "venue": venue,
                "city": city,
                "country": "Japan",
                "lat": lat,
                "lng": lng,
                "start_date": start,
                "end_date": end,
                "ticket_url": "https://www.shiki.jp" + (st.get("applause_url") or "/"),
                "image": ("https://www.shiki.jp" + img) if img else None,
                "tour_name": None,
                "verified": True,
                "source": "shiki.jp",
            }
            print(f"  {title[:32]:34s} @ {venue}  {start} – {end}")

    out = {"meta": {"source": "shiki.jp", "count": len(shows),
                    "skipped_national_tour_rows": skipped},
           "shows": list(shows.values())}
    (DATA / "shiki.json").write_text(json.dumps(out, ensure_ascii=False, indent=2),
                                     encoding="utf-8")
    print(f"\nWrote {len(shows)} shows -> data/shiki.json ({skipped} national-tour rows skipped)")


if __name__ == "__main__":
    main()
