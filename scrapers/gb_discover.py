"""Deep discovery of UK performance venues (Google Places) — every touring city's
theatres / concert halls, same method as na_discover.py (Google is the source).

Run: python -u scrapers/gb_discover.py
Out: data/gb_discovered.json  [{native, en, city, country, lat, lng}]
"""

import json
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
KEEP_TYPES = {"performing_arts_theater", "concert_hall", "opera_house", "auditorium", "amphitheatre"}
MIN_REVIEWS = 120

CITIES = """London;Manchester;Birmingham;Glasgow;Edinburgh;Leeds;Liverpool;Bristol;Cardiff;Nottingham;
Sheffield;Newcastle upon Tyne;Sunderland;Leicester;Coventry;Hull;Bradford;Plymouth;Southampton;Portsmouth;
Brighton;Bournemouth;Oxford;Cambridge;Norwich;Milton Keynes;Northampton;Stoke-on-Trent;Wolverhampton;Derby;
Aberdeen;Dundee;Inverness;Belfast;Swansea;Llandudno;Bath;Cheltenham;Gloucester;Blackpool;York;Woking;
Croydon;Dartford;High Wycombe;Aylesbury;Reading;Swindon;Exeter;Truro;Canterbury;Guildford;Chichester;
Malvern;Stratford-upon-Avon;Wakefield;Bolton;Preston;Lancaster;Carlisle;Middlesbrough;Darlington;Scarborough;
Lincoln;Peterborough;Bedford;Luton;Southend-on-Sea;Chelmsford;Colchester;Ipswich;Eastbourne;Hastings;
Worthing;Poole;Torquay;Hereford;Shrewsbury;Telford;Crewe;Chester;Wigan;Warrington;Barnsley;Doncaster;
Rotherham;Huddersfield;Harrogate;Salford;Newport"""


def search(query, key):
    body = json.dumps({"textQuery": query, "languageCode": "en", "maxResultCount": 20}).encode()
    req = urllib.request.Request(SEARCH, data=body, method="POST", headers={
        "Content-Type": "application/json", "X-Goog-Api-Key": key,
        "X-Goog-FieldMask": "places.displayName,places.location,places.types,places.userRatingCount"})
    try:
        return json.loads(urllib.request.urlopen(req, timeout=25).read()).get("places", [])
    except Exception as e:
        print(f"  [err] {query!r}: {e}", flush=True); return []


def main():
    key = gg.load_key()
    cities = [c.strip() for c in CITIES.replace("\n", "").split(";") if c.strip()]
    qwords = ["theatre", "opera house", "concert hall", "playhouse"]
    found = {}
    print(f"discovering {len(cities)} UK cities", flush=True)
    for ci, city in enumerate(cities, 1):
        for q in qwords:
            for p in search(f"{q} in {city}, United Kingdom", key):
                types = set(p.get("types") or [])
                if not (types & KEEP_TYPES) or (p.get("userRatingCount") or 0) < MIN_REVIEWS:
                    continue
                loc = p.get("location") or {}
                if "latitude" not in loc:
                    continue
                lk = (round(loc["latitude"], 4), round(loc["longitude"], 4))
                nm = (p.get("displayName") or {}).get("text", "")
                rec = found.setdefault(lk, {"native": "", "en": "", "city": city, "country": "UK",
                                            "lat": round(loc["latitude"], 6), "lng": round(loc["longitude"], 6)})
                rec["en"] = rec["en"] or nm
            time.sleep(0.05)
        if ci % 15 == 0:
            print(f"  …{ci}/{len(cities)} cities, {len(found)} venues so far", flush=True)

    recs = [r for r in found.values() if r["en"]]
    (DATA / "gb_discovered.json").write_text(json.dumps(recs, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nDONE: {len(recs)} venues -> data/gb_discovered.json", flush=True)


if __name__ == "__main__":
    main()
