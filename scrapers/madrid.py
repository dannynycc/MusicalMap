"""Madrid musicals — source: teatromadrid.com (WordPress, server-rendered).

Listing items carry title, venue, run dates (Desde/Hasta dd/mm/yyyy), poster
and detail link. Spanish marketing titles are mapped to canonical titles so
they merge with the same show worldwide (El Rey León → The Lion King,
Sonrisas y lágrimas → The Sound of Music, Cenicienta → Cinderella …); the
generic ", el musical" suffix is stripped before lookup.

Output: data/madrid.json   Run: python scrapers/madrid.py
"""

import html as htmllib
import json
import re
import sys
import io
import unicodedata
import urllib.request
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent))
from geocode import geocode  # noqa: E402

DATA = Path(__file__).resolve().parent.parent / "data"
PAGE = ("https://teatromadrid.com/cartelera-teatro-madrid/pagina/{n}"
        "/f/list/popular/14/0/all/0:0/all/all/0/0/0")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) MusicalMap/0.1"

# Spanish marketing title -> canonical worldwide title (match on accent-less lowercase)
TITLES_ES = {
    "los miserables": "Les Misérables",
    "el rey leon": "The Lion King",
    "cenicienta": "Cinderella",
    "sonrisas y lagrimas": "The Sound of Music",
    "six": "SIX",
    "wicked": "Wicked",
    "la sirenita": "The Little Mermaid",
    "el medico": "El Médico (The Physician)",
    "mamma mia": "Mamma Mia!",
    "el fantasma de la opera": "The Phantom of the Opera",
    "la bella y la bestia": "Beauty and the Beast",
    "aladdin": "Aladdin",
    "matilda": "Matilda The Musical",
    "grease": "Grease",
    "chicago": "Chicago",
}


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    return urllib.request.urlopen(req, timeout=40).read().decode("utf-8", "ignore")


def deaccent(t):
    return unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode().lower().strip()


def canon(title_es):
    base = re.sub(r"[,.]?\s*el\s+musical\s*$", "", title_es.strip(), flags=re.I)
    base = re.sub(r"[,.]?\s*the\s+musical\s*$", "", base, flags=re.I).strip()
    return TITLES_ES.get(deaccent(base), base)


def iso(d):
    m = re.match(r"(\d{2})/(\d{2})/(\d{4})", d)
    return f"{m.group(3)}-{m.group(2)}-{m.group(1)}" if m else None


def main():
    shows = {}
    for n in range(1, 7):
        try:
            html = fetch(PAGE.format(n=n))
        except Exception as e:  # noqa: BLE001
            print(f"  [page {n}] {e}")
            break
        items = re.findall(r'<div class="funcion-item-list[^"]*">(.*?)'
                           r'(?=<div class="funcion-item-list|<div class="paginat|$)', html, re.S)
        if not items:
            break
        for it in items:
            dt = re.search(r'data-title="([^"]+)"', it)
            href = re.search(r'href="(https://teatromadrid\.com/espectaculo/[^"]+?)(?:\?[^"]*)?"', it)
            if not dt or not href:
                continue
            raw = htmllib.unescape(dt.group(1))
            parts = re.split(r"\s*(?:→|→)\s*", raw)
            title_es = parts[0].strip()
            venue = (parts[1].strip() if len(parts) > 1 else "")
            dates = re.findall(r"(\d{2}/\d{2}/\d{4})", re.sub(r"<[^>]+>", " ", it))
            start = iso(dates[0]) if dates else None
            end = iso(dates[1]) if len(dates) > 1 else None
            img = re.search(r'(?:data-src|src)="(https://teatromadrid\.com/wp-content/uploads/[^"]+\.(?:jpg|jpeg|png|webp))"', it)
            title = canon(title_es)
            if "por confirmar" in venue.lower():
                continue  # venue TBC — nothing to place on a map yet
            lat, lng = geocode(f"{deaccent(venue)}|madrid", f"{venue}, Madrid, Spain")
            if lat is None:
                continue  # precision over volume: never pile unknowns on the city centre
            sid = "mad-" + re.sub(r"[^a-z0-9]+", "-", href.group(1).split("/espectaculo/")[1].lower()).strip("-")
            shows[sid] = {
                "id": sid, "title": title, "type": "tour",
                "venue": venue or "Madrid", "city": "Madrid", "country": "Spain",
                "lat": lat, "lng": lng,
                "start_date": start, "end_date": end,
                "ticket_url": href.group(1),
                "image": img.group(1) if img else None,
                "tour_name": (f"{title_es}（西語版）" if title != title_es else None),
                "verified": True, "source": "teatromadrid.com",
            }
            print(f"  {title_es[:30]:32s} -> {title[:26]:28s} @ {venue[:26]:28s} {start}~{end}")

    out = {"meta": {"source": "teatromadrid.com", "count": len(shows)}, "shows": list(shows.values())}
    (DATA / "madrid.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nWrote {len(shows)} shows -> data/madrid.json")


if __name__ == "__main__":
    main()
