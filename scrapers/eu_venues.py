"""Curated European (+ Russia) musical-theatre venues.

The houses that actually stage big musicals across Europe — Stage Entertainment
theatres, national operetta/musical houses, and the main touring receiving
theatres. Each is Google-geocoded for a building-level coordinate AND given both
its English name and its local-language name, so a user can search in either
(English or local script — incl. Greek / Cyrillic). Populates the My-Musicals
autocomplete (no "currently playing" run → not on the world map).

Run: python -u scrapers/eu_venues.py   (incremental; --all to redo)
Out: data/eu_venues.json  [{native, en, city, country, lat, lng}]
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

LANG = {  # local language code for the native place name
    "Germany": "de", "France": "fr", "Italy": "it", "Spain": "es", "Netherlands": "nl",
    "Belgium": "nl", "Sweden": "sv", "Denmark": "da", "Norway": "no", "Finland": "fi",
    "Poland": "pl", "Czech Republic": "cs", "Hungary": "hu", "Austria": "de",
    "Slovakia": "sk", "Slovenia": "sl", "Croatia": "hr", "Greece": "el", "Russia": "ru",
}

# (city, country, geocode query)
VENUES = [
    # Germany — Stage Entertainment + major musical houses
    ("Hamburg", "Germany", "Stage Theater im Hafen Hamburg"),
    ("Hamburg", "Germany", "Stage Theater an der Elbe, Hamburg"),
    ("Hamburg", "Germany", "Stage Operettenhaus, Hamburg"),
    ("Hamburg", "Germany", "Mehr! Theater am Großmarkt, Hamburg"),
    ("Berlin", "Germany", "Theater des Westens, Berlin"),
    ("Berlin", "Germany", "Stage Theater am Potsdamer Platz, Berlin"),
    ("Berlin", "Germany", "Admiralspalast, Berlin"),
    ("Stuttgart", "Germany", "Stage Apollo Theater, Stuttgart"),
    ("Stuttgart", "Germany", "Stage Palladium Theater, Stuttgart"),
    ("Cologne", "Germany", "Musical Dome, Köln"),
    ("Oberhausen", "Germany", "Stage Metronom Theater, Oberhausen"),
    ("Munich", "Germany", "Deutsches Theater München"),
    ("Düsseldorf", "Germany", "Capitol Theater, Düsseldorf"),
    # France
    ("Paris", "France", "Théâtre Mogador, Paris"),
    ("Paris", "France", "Le Palace, Paris"),
    ("Paris", "France", "Folies Bergère, Paris"),
    ("Paris", "France", "Théâtre de Paris"),
    ("Paris", "France", "Casino de Paris"),
    ("Paris", "France", "Théâtre Marigny, Paris"),
    ("Paris", "France", "Palais des Congrès de Paris"),
    ("Boulogne-Billancourt", "France", "La Seine Musicale, Boulogne-Billancourt"),
    # Italy
    ("Milan", "Italy", "Teatro degli Arcimboldi, Milano"),
    ("Milan", "Italy", "Teatro Nazionale, Milano"),
    ("Milan", "Italy", "Teatro Manzoni, Milano"),
    ("Rome", "Italy", "Teatro Sistina, Roma"),
    ("Rome", "Italy", "Teatro Brancaccio, Roma"),
    # Spain — Barcelona (Madrid already covered elsewhere)
    ("Barcelona", "Spain", "Teatre Tívoli, Barcelona"),
    ("Barcelona", "Spain", "Teatre Victòria, Barcelona"),
    ("Barcelona", "Spain", "BARTS Barcelona"),
    ("Barcelona", "Spain", "Teatre Apolo, Barcelona"),
    ("Barcelona", "Spain", "Gran Teatre del Liceu, Barcelona"),
    ("Barcelona", "Spain", "Teatre Coliseum, Barcelona"),
    # Netherlands
    ("Amsterdam", "Netherlands", "DeLaMar Theater, Amsterdam"),
    ("Amsterdam", "Netherlands", "Koninklijk Theater Carré, Amsterdam"),
    ("Amsterdam", "Netherlands", "AFAS Live, Amsterdam"),
    ("Utrecht", "Netherlands", "Beatrix Theater, Utrecht"),
    ("The Hague", "Netherlands", "AFAS Circustheater, Scheveningen"),
    # Belgium
    ("Antwerp", "Belgium", "Stadsschouwburg Antwerpen"),
    ("Brussels", "Belgium", "Cirque Royal, Brussels"),
    ("Brussels", "Belgium", "Forest National, Brussels"),
    # Sweden
    ("Stockholm", "Sweden", "Oscarsteatern, Stockholm"),
    ("Stockholm", "Sweden", "China Teatern, Stockholm"),
    ("Stockholm", "Sweden", "Göta Lejon, Stockholm"),
    ("Stockholm", "Sweden", "Cirkus, Stockholm"),
    # Denmark
    ("Copenhagen", "Denmark", "Tivoli Koncertsal, Copenhagen"),
    ("Copenhagen", "Denmark", "Operaen, Copenhagen Opera House"),
    # Norway
    ("Oslo", "Norway", "Folketeateret, Oslo"),
    ("Oslo", "Norway", "Det Norske Teatret, Oslo"),
    # Finland
    ("Helsinki", "Finland", "Svenska Teatern, Helsinki"),
    ("Helsinki", "Finland", "Helsingin kaupunginteatteri Helsinki City Theatre"),
    ("Tampere", "Finland", "Tampere-talo, Tampere"),
    # Poland
    ("Warsaw", "Poland", "Teatr Muzyczny Roma, Warszawa"),
    ("Warsaw", "Poland", "Teatr Wielki, Warszawa"),
    ("Gdynia", "Poland", "Teatr Muzyczny w Gdyni"),
    ("Chorzów", "Poland", "Teatr Rozrywki, Chorzów"),
    ("Łódź", "Poland", "Teatr Muzyczny w Łodzi"),
    # Czech Republic
    ("Prague", "Czech Republic", "Hudební divadlo Karlín, Praha"),
    ("Prague", "Czech Republic", "GOJA Music Hall, Praha"),
    ("Prague", "Czech Republic", "Divadlo Broadway, Praha"),
    ("Prague", "Czech Republic", "Divadlo Hybernia, Praha"),
    # Hungary
    ("Budapest", "Hungary", "Madách Színház, Budapest"),
    ("Budapest", "Hungary", "Budapesti Operettszínház"),
    ("Budapest", "Hungary", "Erkel Színház, Budapest"),
    ("Budapest", "Hungary", "Papp László Budapest Sportaréna"),
    # Austria
    ("Vienna", "Austria", "Theater an der Wien"),
    ("Vienna", "Austria", "Ronacher, Wien"),
    ("Vienna", "Austria", "Raimund Theater, Wien"),
    # Slovakia
    ("Bratislava", "Slovakia", "Nová scéna, Bratislava"),
    ("Bratislava", "Slovakia", "Slovenské národné divadlo, Bratislava"),
    # Slovenia
    ("Ljubljana", "Slovenia", "Cankarjev dom, Ljubljana"),
    ("Ljubljana", "Slovenia", "SNG Opera in balet Ljubljana"),
    # Croatia
    ("Zagreb", "Croatia", "Kazalište Komedija, Zagreb"),
    ("Zagreb", "Croatia", "Hrvatsko narodno kazalište u Zagrebu"),
    ("Zagreb", "Croatia", "Koncertna dvorana Vatroslava Lisinskog, Zagreb"),
    # Greece
    ("Athens", "Greece", "Pallas Theatre, Athens"),
    ("Athens", "Greece", "Megaron Athens Concert Hall"),
    ("Athens", "Greece", "Christmas Theater, Athens"),
    ("Athens", "Greece", "Badminton Theater, Athens"),
    # Russia
    ("Moscow", "Russia", "Театр МДМ, Москва"),
    ("Moscow", "Russia", "Московский театр оперетты"),
    ("Moscow", "Russia", "Crocus City Hall, Moscow"),
    ("Saint Petersburg", "Russia", "Санкт-Петербургский театр музыкальной комедии"),
]


def name_in(query, key, lang):
    r = gg.places_new(query, key, language=lang)
    if isinstance(r, tuple) and r and r[0] != "DENIED" and len(r) >= 3:
        return r[2]
    return None


def main():
    key = gg.load_key()
    force = "--all" in sys.argv
    out_path = DATA / "eu_venues.json"
    existing = {v["_q"]: v for v in json.loads(out_path.read_text(encoding="utf-8"))} if out_path.exists() else {}

    out = []
    print(f"geocoding {len(VENUES)} European venues", flush=True)
    for i, (city, country, query) in enumerate(VENUES, 1):
        if not force and query in existing and existing[query].get("lat"):
            out.append(existing[query]); continue
        r = gg.places_new(query, key)
        time.sleep(0.06)
        if isinstance(r, tuple) and r and r[0] != "DENIED" and len(r) >= 5:
            lat, lng = round(r[0], 6), round(r[1], 6)
            en = name_in(query, key, "en") or r[2]; time.sleep(0.06)
            native = name_in(query, key, LANG.get(country, "en")) or r[2]; time.sleep(0.06)
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
    print(f"\nDONE: {ok}/{len(out)} geocoded -> data/eu_venues.json", flush=True)


if __name__ == "__main__":
    main()
