"""Deep discovery of European performance venues via Google Places Text Search.

We don't invent venues — Google is the source. For a wide list of European cities
we Text-Search for theatres / concert halls / opera houses, keep only results whose
Google place *type* is a performance venue with enough reviews (skips obscure /
wrong hits), and record English + (for Greek/Cyrillic) native names + coordinates.
Output is deduped against the curated lists by the catalog build.

Run: python -u scrapers/eu_discover.py   (incremental; --all to redo)
Out: data/eu_discovered.json  [{native, en, city, country, lat, lng}]
"""

import json
import math
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
import importlib.util
_spec = importlib.util.spec_from_file_location("gg", ROOT / "scrapers" / "geocode_google.py")
gg = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(gg)

SEARCH = "https://places.googleapis.com/v1/places:searchText"
KEEP_TYPES = {"performing_arts_theater", "concert_hall", "opera_house", "auditorium",
              "amphitheatre", "event_venue", "arena"}
MIN_REVIEWS = 150

# (city, country, local-language code) — broad sweep; big countries get many cities.
CITIES = [
    ("Hamburg","Germany","de"),("Berlin","Germany","de"),("Munich","Germany","de"),
    ("Cologne","Germany","de"),("Stuttgart","Germany","de"),("Frankfurt","Germany","de"),
    ("Düsseldorf","Germany","de"),("Dortmund","Germany","de"),("Essen","Germany","de"),
    ("Leipzig","Germany","de"),("Dresden","Germany","de"),("Hannover","Germany","de"),
    ("Nuremberg","Germany","de"),("Bremen","Germany","de"),("Bonn","Germany","de"),
    ("Oberhausen","Germany","de"),("Mannheim","Germany","de"),("Bochum","Germany","de"),
    ("Paris","France","fr"),("Lyon","France","fr"),("Marseille","France","fr"),
    ("Toulouse","France","fr"),("Lille","France","fr"),("Bordeaux","France","fr"),
    ("Nice","France","fr"),("Nantes","France","fr"),("Strasbourg","France","fr"),
    ("Milan","Italy","it"),("Rome","Italy","it"),("Naples","Italy","it"),("Turin","Italy","it"),
    ("Bologna","Italy","it"),("Florence","Italy","it"),("Genoa","Italy","it"),("Verona","Italy","it"),
    ("Barcelona","Spain","es"),("Madrid","Spain","es"),("Valencia","Spain","es"),
    ("Seville","Spain","es"),("Bilbao","Spain","es"),("Málaga","Spain","es"),
    ("Amsterdam","Netherlands","nl"),("Rotterdam","Netherlands","nl"),("Utrecht","Netherlands","nl"),
    ("The Hague","Netherlands","nl"),("Eindhoven","Netherlands","nl"),
    ("Brussels","Belgium","nl"),("Antwerp","Belgium","nl"),("Ghent","Belgium","nl"),
    ("Stockholm","Sweden","sv"),("Gothenburg","Sweden","sv"),("Malmö","Sweden","sv"),
    ("Copenhagen","Denmark","da"),("Aarhus","Denmark","da"),
    ("Oslo","Norway","no"),("Bergen","Norway","no"),
    ("Helsinki","Finland","fi"),("Tampere","Finland","fi"),("Turku","Finland","fi"),
    ("Warsaw","Poland","pl"),("Kraków","Poland","pl"),("Wrocław","Poland","pl"),
    ("Poznań","Poland","pl"),("Gdynia","Poland","pl"),("Łódź","Poland","pl"),("Chorzów","Poland","pl"),
    ("Prague","Czech Republic","cs"),("Brno","Czech Republic","cs"),("Ostrava","Czech Republic","cs"),
    ("Budapest","Hungary","hu"),("Szeged","Hungary","hu"),("Debrecen","Hungary","hu"),
    ("Vienna","Austria","de"),("Graz","Austria","de"),("Linz","Austria","de"),("Salzburg","Austria","de"),
    ("Bratislava","Slovakia","sk"),("Košice","Slovakia","sk"),
    ("Ljubljana","Slovenia","sl"),("Maribor","Slovenia","sl"),
    ("Zagreb","Croatia","hr"),("Split","Croatia","hr"),("Rijeka","Croatia","hr"),
    ("Athens","Greece","el"),("Thessaloniki","Greece","el"),
    ("Moscow","Russia","ru"),("Saint Petersburg","Russia","ru"),
    ("Novosibirsk","Russia","ru"),("Yekaterinburg","Russia","ru"),
    ("Lisbon","Portugal","pt"),("Porto","Portugal","pt"),
    ("Zurich","Switzerland","de"),("Geneva","Switzerland","fr"),("Basel","Switzerland","de"),
    ("Bucharest","Romania","ro"),("Sofia","Bulgaria","bg"),("Tallinn","Estonia","et"),
    ("Riga","Latvia","lv"),("Vilnius","Lithuania","lt"),("Belgrade","Serbia","sr"),
]


def search(query, key, lang):
    body = json.dumps({"textQuery": query, "languageCode": lang, "maxResultCount": 20}).encode()
    req = urllib.request.Request(SEARCH, data=body, method="POST", headers={
        "Content-Type": "application/json", "X-Goog-Api-Key": key,
        "X-Goog-FieldMask": "places.displayName,places.location,places.types,places.userRatingCount"})
    try:
        return json.loads(urllib.request.urlopen(req, timeout=25).read()).get("places", [])
    except Exception as e:
        print(f"  [err] {query!r}: {e}", flush=True); return []


def dist_m(a, b, c, d):
    R = 6371008.8; p = math.pi / 180
    h = 0.5 - math.cos((c-a)*p)/2 + math.cos(a*p)*math.cos(c*p)*(1-math.cos((d-b)*p))/2
    return 2*R*math.asin(math.sqrt(h))


def main():
    key = gg.load_key()
    out_path = DATA / "eu_discovered.json"
    found = {}   # (round lat,lng) -> rec, dedupe by location
    qwords = ["theatre", "concert hall", "opera house", "musical theatre"]
    print(f"discovering across {len(CITIES)} cities", flush=True)
    for ci, (city, country, lang) in enumerate(CITIES, 1):
        native_only = lang in ("el", "ru")     # Greek / Cyrillic → also grab native script
        for q in qwords:
            for code in (["en", lang] if native_only else ["en"]):
                for p in search(f"{q} in {city}, {country}", key, code):
                    types = set(p.get("types") or [])
                    if not (types & KEEP_TYPES) or (p.get("userRatingCount") or 0) < MIN_REVIEWS:
                        continue
                    loc = p.get("location") or {}
                    if "latitude" not in loc:
                        continue
                    lk = (round(loc["latitude"], 4), round(loc["longitude"], 4))
                    nm = (p.get("displayName") or {}).get("text", "")
                    rec = found.setdefault(lk, {"native": "", "en": "", "city": city,
                                                "country": country, "lat": round(loc["latitude"], 6),
                                                "lng": round(loc["longitude"], 6)})
                    if code == "en":
                        rec["en"] = rec["en"] or nm
                    else:
                        rec["native"] = rec["native"] or nm
                time.sleep(0.05)
        if ci % 10 == 0:
            print(f"  …{ci}/{len(CITIES)} cities, {len(found)} venues so far", flush=True)

    recs = [r for r in found.values() if r["en"] or r["native"]]
    out_path.write_text(json.dumps(recs, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nDONE: {len(recs)} performance venues -> data/eu_discovered.json", flush=True)


if __name__ == "__main__":
    main()
