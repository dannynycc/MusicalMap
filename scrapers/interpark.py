"""韓國 Interpark (NOL / world.nol.com) musicals — open JSON API.

API: /api/ent-channel-out/v1/goods/list?genreType=MUSICAL (paginated, no auth).
Gives REAL run dates (playStartDate/playEndDate — actual opening, unlike
Ticketmaster's availability window), venue name and posters. No coordinates —
we use a known-venue table for the major Korean houses plus Nominatim fallback
(", Seoul, South Korea" first — most are Seoul — then ", South Korea");
records that still fail are dropped and reported, never guessed.

Output: data/interpark.json   Run: python scrapers/interpark.py
"""

import json
import re
import sys
import io
import urllib.request
import urllib.parse
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent))
from geocode import geocode  # noqa: E402

DATA = Path(__file__).resolve().parent.parent / "data"
API = "https://world.nol.com/api/ent-channel-out/v1/goods/list"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) MusicalMap/0.1"

# Major Korean venues (stable). Substring match, lowercase.
VENUES = {
    "blue square": ("BLUE SQUARE", "Seoul", 37.5409, 127.0028),
    "charlotte theater": ("Charlotte Theater", "Seoul", 37.5111, 127.0996),
    "lg arts center": ("LG Arts Center Seoul", "Seoul", 37.5664, 126.8270),
    "sejong": ("Sejong Center", "Seoul", 37.5725, 126.9760),
    "chungmu arts center": ("Chungmu Arts Center", "Seoul", 37.5663, 127.0181),
    "coex": ("Coex Artium", "Seoul", 37.5126, 127.0588),
    "uniplex": ("NOL Uniplex (大學路)", "Seoul", 37.5821, 127.0019),
    "yes24 art one": ("YES24 ART ONE (大學路)", "Seoul", 37.5817, 127.0034),
    "yes24 stage": ("YES24 Stage (大學路)", "Seoul", 37.5808, 127.0040),
    "national theater of korea": ("The National Theater of Korea", "Seoul", 37.5520, 127.0086),
    "seoul arts center": ("Seoul Arts Center", "Seoul", 37.4786, 127.0119),
    "doosan art center": ("Doosan Art Center", "Seoul", 37.5694, 127.0167),
    "hongik": ("Hongik Daehangno Art Center", "Seoul", 37.5797, 127.0035),
    "kwanglim": ("Kwanglim Arts Center", "Seoul", 37.5172, 127.0399),
    "myungbo art hall": ("Myungbo Art Hall", "Seoul", 37.5654, 126.9936),
    "dream art center": ("Dream Art Center (大學路)", "Seoul", 37.5810, 127.0048),
    "daehangno": ("大學路", "Seoul", 37.5817, 127.0027),
    "dae hak no": ("大學路 Art Madang", "Seoul", 37.5811, 127.0049),
    "mckithan": ("The McKithan Hotel (舊大韓劇場, 忠武路)", "Seoul", 37.5613, 126.9947),
    "galleria foret": ("Seoul Forest Galleria Foret", "Seoul", 37.5447, 127.0436),
    "jtn art hall": ("JTN Art Hall (大學路)", "Seoul", 37.5824, 127.0043),
    "myeongnyun art hall": ("Myeongnyun Art Hall", "Seoul", 37.5837, 126.9985),
    "myeongdong art center": ("Myeongdong NANTA Theater", "Seoul", 37.5636, 126.9869),
    "hongdae nanta": ("Hongdae NANTA Theater", "Seoul", 37.5571, 126.9244),
    "kyounghyang art hill": ("Kyounghyang Art Hill (貞洞)", "Seoul", 37.5560, 126.9716),
    # Daegu (DIMF circuit)
    "suseong artpia": ("Suseong Artpia", "Daegu", 35.8419, 128.6190),
    "ayang art center": ("Daegu Ayang Art Center", "Daegu", 35.8854, 128.6357),
    "bongsan cultural center": ("Daegu Bongsan Cultural Center", "Daegu", 35.8579, 128.5945),
    "daegu culture & arts centre": ("Daegu Culture & Arts Centre", "Daegu", 35.8533, 128.5586),
    "cgv daegu hanil": ("CGV Daegu Hanil", "Daegu", 35.8696, 128.5942),
}
KOREAN_CITIES = ["Seoul", "Busan", "Daegu", "Daejeon", "Incheon", "Gwangju", "Ulsan", "Suwon", "Goyang"]


# Service/merch products that NOL lists under MUSICAL but are not shows
JUNK = re.compile(r"caption\s*glasses|rental|자막|렌탈|주차|parking|package|패키지|"
                  r"goods|md\b|gift\s*card", re.I)


def clean_title(name):
    t = (name or "").strip()
    t = re.sub(r"^\s*(show\s+musical|musical\s*pub|musical|뮤지컬)\s*", "", t, flags=re.I)
    t = t.strip()
    t = re.sub(r"^[〈\[<(]\s*", "", t)
    t = re.sub(r"\s*[〉\]>)]\s*$", "", t)
    t = t.replace("〈", " ").replace("〉", " ").strip()
    return t or name.strip()


def city_hint(name):
    for c in KOREAN_CITIES[1:]:
        if re.search(rf"(?:^|[-–(\s]){c}\b", name, re.I):
            return c
    return None


def fetch_page(page):
    qs = urllib.parse.urlencode({
        "goodsStatus": "Y,D", "globalType": "EN", "languageType": "EN",
        "genreType": "MUSICAL", "page": page, "size": 15, "includeNonPartnerGoods": "true",
    })
    req = urllib.request.Request(f"{API}?{qs}", headers={"User-Agent": UA})
    return json.loads(urllib.request.urlopen(req, timeout=30).read().decode("utf-8"))["data"]


def main():
    # NOTE: the API silently caps page size (requesting 50 still returns ~15),
    # and totalPages is computed from the REQUESTED size — don't trust it.
    # Page until empty / until we've collected totalElements.
    page, items, total = 1, [], None
    while page < 40:
        d = fetch_page(page)
        batch = d["content"]
        total = d.get("totalElements") or total
        if not batch:
            break
        items += batch
        if total and len(items) >= total:
            break
        page += 1
    print(f"{len(items)} musicals from NOL/Interpark API")

    shows, missing = [], []
    for it in items:
        raw_title = it.get("goodsName") or ""
        if JUNK.search(raw_title):
            continue  # caption-glasses rental / parking / merch — not a show
        title = clean_title(raw_title)
        place = (it.get("placeName") or "").strip()
        if not title or not place:
            continue
        city = city_hint(raw_title) or city_hint(place)
        vk = next((v for k, v in VENUES.items() if k in place.lower()), None)
        if vk:
            venue, vcity, lat, lng = vk
            city = city or vcity
        else:
            venue = place
            city = city or "Seoul"
            lat, lng = geocode(f"{place}|{city}|kr".lower(), f"{place}, {city}, South Korea")
            if lat is None:
                lat, lng = geocode(f"{place}|kr".lower(), f"{place}, South Korea")
        if lat is None:
            missing.append(f"{title} @ {place}")
            continue  # never guess a position

        gc, pc = it.get("goodsCode"), it.get("placeCode")
        shows.append({
            "id": f"ip-{gc}",
            "title": title,
            "type": "tour",  # limited licensed seasons — card shows the real run range
            "venue": venue,
            "city": city,
            "country": "South Korea",
            "lat": lat,
            "lng": lng,
            "start_date": it.get("playStartDate") or None,
            "end_date": it.get("playEndDate") or None,
            "ticket_url": f"https://world.nol.com/en/ticket/places/{pc}/products/{gc}",
            # posterImageUrl (…_p.gif) is the live poster; goodsLargeImageUrl often 404s
            "image": it.get("posterImageUrl") or it.get("goodsLargeImageUrl") or it.get("goodsSmallImageUrl"),
            "tour_name": None,
            "verified": True,
            "source": "world.nol.com (Interpark)",
        })

    out = {"meta": {"source": "world.nol.com (Interpark)", "count": len(shows),
                    "dropped_no_coords": missing}, "shows": shows}
    (DATA / "interpark.json").write_text(json.dumps(out, ensure_ascii=False, indent=2),
                                         encoding="utf-8")
    print(f"Wrote {len(shows)} shows -> data/interpark.json")
    if missing:
        print(f"⚠ dropped (no coords): {len(missing)}")
        for m in missing[:10]:
            print("   ", m)


if __name__ == "__main__":
    main()
