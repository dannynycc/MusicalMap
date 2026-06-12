"""Deep discovery of North America + Oceania performance venues (Google Places).

Same method as eu_discover.py: Google is the source (no invented venues). For a
wide list of US / Canada / Australia / New Zealand cities we Text-Search for
theatres / performing-arts centers / concert halls / opera houses, keep only
results whose Google place *type* is a performance venue with >=150 reviews, and
record name + coordinates. Deduped against everything by the catalog build.

Run: python -u scrapers/na_discover.py   (incremental; --all to redo)
Out: data/na_discovered.json  [{native, en, city, country, lat, lng}]
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
MIN_REVIEWS = 150

US = """New York;Chicago;Los Angeles;San Francisco;Boston;Washington;Philadelphia;Atlanta;Seattle;
Houston;Dallas;Austin;San Antonio;Fort Worth;El Paso;Denver;Phoenix;Tucson;Las Vegas;Miami;Orlando;
Tampa;Jacksonville;Fort Lauderdale;West Palm Beach;Naples;Sarasota;Tallahassee;Minneapolis;Detroit;
Grand Rapids;Cleveland;Columbus;Cincinnati;Dayton;Toledo;Akron;Pittsburgh;Baltimore;Charlotte;Raleigh;
Durham;Greensboro;Nashville;Memphis;Knoxville;Chattanooga;New Orleans;Baton Rouge;Shreveport;St. Louis;
Kansas City;Milwaukee;Madison;Green Bay;Appleton;Indianapolis;Fort Wayne;South Bend;Bloomington;Louisville;
Lexington;Portland;Eugene;Salt Lake City;San Diego;Sacramento;San Jose;Costa Mesa;Anaheim;Fresno;Bakersfield;
Buffalo;Rochester;Syracuse;Albany;Hartford;New Haven;Stamford;Providence;Worcester;Springfield;Portland ME;
Manchester NH;Richmond;Norfolk;Charleston;Savannah;Columbia;Greenville;Birmingham;Huntsville;Montgomery;Mobile;
Pensacola;Little Rock;Tulsa;Oklahoma City;Omaha;Lincoln;Des Moines;Wichita;Boise;Spokane;Tacoma;Reno;
Albuquerque;Colorado Springs;Boulder;Lubbock;Corpus Christi;McAllen;Jackson;Newark;Atlantic City;
East Lansing;Ann Arbor;Kalamazoo;Peoria;Champaign;Allentown;Scranton;Harrisburg;Erie;Honolulu;Anchorage;
Cedar Rapids;Fargo;Sioux Falls;Duluth;Wilmington;Akron"""

OTHER = {
    "Canada": "Toronto;Montreal;Vancouver;Calgary;Edmonton;Ottawa;Winnipeg;Quebec City;Hamilton;"
              "London;Halifax;Victoria;Kitchener;Mississauga;Saskatoon;Regina;St. John's",
    "Australia": "Sydney;Melbourne;Brisbane;Perth;Adelaide;Canberra;Gold Coast;Newcastle;Wollongong;"
                 "Hobart;Darwin;Geelong;Cairns;Townsville",
    "New Zealand": "Auckland;Wellington;Christchurch;Dunedin;Hamilton;Tauranga;Palmerston North",
}


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
    cities = [(c.strip(), "USA") for c in US.replace("\n", "").split(";") if c.strip()]
    for country, lst in OTHER.items():
        cities += [(c.strip(), country) for c in lst.split(";") if c.strip()]

    qwords = ["performing arts center", "theatre", "concert hall", "opera house"]
    found = {}
    print(f"discovering across {len(cities)} cities", flush=True)
    for ci, (city, country) in enumerate(cities, 1):
        for q in qwords:
            for p in search(f"{q} in {city}, {country}", key):
                types = set(p.get("types") or [])
                if not (types & KEEP_TYPES) or (p.get("userRatingCount") or 0) < MIN_REVIEWS:
                    continue
                loc = p.get("location") or {}
                if "latitude" not in loc:
                    continue
                lk = (round(loc["latitude"], 4), round(loc["longitude"], 4))
                nm = (p.get("displayName") or {}).get("text", "")
                rec = found.setdefault(lk, {"native": "", "en": "", "city": city, "country": country,
                                            "lat": round(loc["latitude"], 6), "lng": round(loc["longitude"], 6)})
                rec["en"] = rec["en"] or nm
            time.sleep(0.05)
        if ci % 15 == 0:
            print(f"  …{ci}/{len(cities)} cities, {len(found)} venues so far", flush=True)

    recs = [r for r in found.values() if r["en"]]
    (DATA / "na_discovered.json").write_text(json.dumps(recs, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nDONE: {len(recs)} venues -> data/na_discovered.json", flush=True)


if __name__ == "__main__":
    main()
