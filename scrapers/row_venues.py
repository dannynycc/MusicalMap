"""Rest-of-world KEY musical/large-show venues (curated highlights, not a deep crawl).

Covers regions thin in the dataset — Latin America, Middle East, India, SE-Asia,
Africa, Turkey — with each country's handful of flagship houses that stage big
musicals / international tours. Google-geocoded (building-level) with English +
local-language names so either script searches.

Run: python -u scrapers/row_venues.py   (incremental; --all to redo)
Out: data/row_venues.json  [{native, en, city, country, lat, lng}]
"""

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
import importlib.util
_spec = importlib.util.spec_from_file_location("gg", ROOT / "scrapers" / "geocode_google.py")
gg = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(gg)

LANG = {"Brazil": "pt", "Argentina": "es", "Chile": "es", "Mexico": "es", "Colombia": "es",
        "Peru": "es", "Israel": "iw", "United Arab Emirates": "en", "India": "en",
        "Indonesia": "id", "Vietnam": "vi", "Thailand": "th", "Egypt": "ar",
        "South Africa": "en", "Turkey": "tr"}

# (city, country, geocode query)
VENUES = [
    # Brazil
    ("São Paulo", "Brazil", "Teatro Renault, São Paulo"),
    ("São Paulo", "Brazil", "Teatro Santander, São Paulo"),
    ("São Paulo", "Brazil", "Teatro Bradesco, São Paulo"),
    ("São Paulo", "Brazil", "Teatro Procópio Ferreira, São Paulo"),
    ("São Paulo", "Brazil", "Teatro Alfa, São Paulo"),
    ("Rio de Janeiro", "Brazil", "Theatro Municipal do Rio de Janeiro"),
    ("Rio de Janeiro", "Brazil", "Vivo Rio, Rio de Janeiro"),
    # Argentina
    ("Buenos Aires", "Argentina", "Teatro Gran Rex, Buenos Aires"),
    ("Buenos Aires", "Argentina", "Teatro Ópera, Buenos Aires"),
    ("Buenos Aires", "Argentina", "Teatro Colón, Buenos Aires"),
    ("Buenos Aires", "Argentina", "Teatro Maipo, Buenos Aires"),
    ("Buenos Aires", "Argentina", "Luna Park, Buenos Aires"),
    # Chile
    ("Santiago", "Chile", "Teatro Municipal de Santiago"),
    ("Santiago", "Chile", "Teatro Nescafé de las Artes, Santiago"),
    ("Santiago", "Chile", "Movistar Arena, Santiago"),
    # Mexico (already a few; add flagships)
    ("Mexico City", "Mexico", "Teatro Telcel, Ciudad de México"),
    ("Mexico City", "Mexico", "Auditorio Nacional, Ciudad de México"),
    ("Mexico City", "Mexico", "Centro Cultural Teatro 1, Ciudad de México"),
    # Colombia / Peru
    ("Bogotá", "Colombia", "Teatro Mayor Julio Mario Santo Domingo, Bogotá"),
    ("Lima", "Peru", "Gran Teatro Nacional, Lima"),
    # Israel
    ("Tel Aviv", "Israel", "Charles Bronfman Auditorium Heichal HaTarbut, Tel Aviv"),
    ("Tel Aviv", "Israel", "Habima Theatre, Tel Aviv"),
    ("Tel Aviv", "Israel", "Cameri Theatre, Tel Aviv"),
    ("Tel Aviv", "Israel", "Menora Mivtachim Arena, Tel Aviv"),
    # UAE
    ("Dubai", "United Arab Emirates", "Dubai Opera"),
    ("Dubai", "United Arab Emirates", "Coca-Cola Arena, Dubai"),
    ("Abu Dhabi", "United Arab Emirates", "Etihad Arena, Abu Dhabi"),
    ("Abu Dhabi", "United Arab Emirates", "Cultural Foundation, Abu Dhabi"),
    # India
    ("Mumbai", "India", "NCPA Jamshed Bhabha Theatre, Mumbai"),
    ("Mumbai", "India", "Royal Opera House, Mumbai"),
    ("Mumbai", "India", "Nita Mukesh Ambani Cultural Centre Grand Theatre, Mumbai"),
    ("New Delhi", "India", "Kamani Auditorium, New Delhi"),
    ("New Delhi", "India", "Siri Fort Auditorium, New Delhi"),
    # Indonesia
    ("Jakarta", "Indonesia", "Ciputra Artpreneur Theater, Jakarta"),
    ("Jakarta", "Indonesia", "Jakarta International Expo Theater"),
    # Vietnam
    ("Ho Chi Minh City", "Vietnam", "Saigon Opera House, Ho Chi Minh City"),
    ("Hanoi", "Vietnam", "Hanoi Opera House"),
    # Thailand extra (flagship already curated; add)
    ("Bangkok", "Thailand", "Thailand Cultural Centre, Bangkok"),
    # Egypt
    ("Cairo", "Egypt", "Cairo Opera House"),
    # South Africa
    ("Cape Town", "South Africa", "Artscape Theatre Centre, Cape Town"),
    ("Johannesburg", "South Africa", "Joburg Theatre, Johannesburg"),
    ("Johannesburg", "South Africa", "Teatro at Montecasino, Johannesburg"),
    ("Pretoria", "South Africa", "South African State Theatre, Pretoria"),
    # Turkey
    ("Istanbul", "Turkey", "Zorlu PSM, Istanbul"),
    ("Istanbul", "Turkey", "Türker İnanoğlu Maslak Show Center, Istanbul"),
    ("Ankara", "Turkey", "MEB Şura Salonu, Ankara"),
]


def nm(query, key, lang):
    r = gg.places_new(query, key, language=lang)
    if isinstance(r, tuple) and r and r[0] != "DENIED" and len(r) >= 3:
        return r[2]
    return None


def main():
    key = gg.load_key()
    force = "--all" in sys.argv
    out_path = DATA / "row_venues.json"
    existing = {v["_q"]: v for v in json.loads(out_path.read_text(encoding="utf-8"))} if out_path.exists() else {}
    out = []
    print(f"geocoding {len(VENUES)} rest-of-world venues", flush=True)
    for i, (city, country, query) in enumerate(VENUES, 1):
        if not force and query in existing and existing[query].get("lat"):
            out.append(existing[query]); continue
        r = gg.places_new(query, key)
        time.sleep(0.06)
        if isinstance(r, tuple) and r and r[0] != "DENIED" and len(r) >= 5:
            lat, lng = round(r[0], 6), round(r[1], 6)
            en = nm(query, key, "en") or r[2]; time.sleep(0.06)
            native = nm(query, key, LANG.get(country, "en")) or ""; time.sleep(0.06)
            if native.strip() == en.strip():
                native = ""
            rec = {"_q": query, "native": native, "en": en, "city": city, "country": country,
                   "lat": lat, "lng": lng}
            print(f"  [{i}/{len(VENUES)}] {en} | {native} @ {lat},{lng}", flush=True)
        else:
            rec = {"_q": query, "native": "", "en": query.split(",")[0], "city": city,
                   "country": country, "lat": None, "lng": None}
            print(f"  [{i}/{len(VENUES)}] {query} → NO RESULT (manual)", flush=True)
        out.append(rec)
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    ok = sum(1 for v in out if v.get("lat"))
    print(f"\nDONE: {ok}/{len(out)} geocoded -> data/row_venues.json", flush=True)


if __name__ == "__main__":
    main()
