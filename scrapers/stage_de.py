"""Stage Entertainment Germany — source: stage-entertainment.de

No public API; the site is server-rendered. Show URLs carry the city in the
slug (/musicals-shows/die-eiskoenigin-stuttgart). We collect show links from
the homepage + each city hub, then read each show page for the theatre name
(Stage owns a fixed set of houses — coordinates hardcoded) and og:image.
Stage productions are open-ended residencies → start/end null (= playing now).

Output: data/stage_de.json   Run: python scrapers/stage_de.py
"""

import html as htmllib
import json
import re
import sys
import io
import time
import urllib.request
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

DATA = Path(__file__).resolve().parent.parent / "data"
BASE = "https://www.stage-entertainment.de"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) MusicalMap/0.1"

CITY_SLUGS = {
    "hamburg": "Hamburg", "berlin": "Berlin", "stuttgart": "Stuttgart",
    "muenchen": "Munich", "koeln": "Cologne", "duesseldorf": "Düsseldorf",
    "oberhausen": "Oberhausen", "essen": "Essen", "bochum": "Bochum",
}
# Stage's own theatres (stable, landmark-level coords)
THEATRES = {
    "theater im hafen": ("Stage Theater im Hafen", 53.5399, 9.9733),
    "theater an der elbe": ("Stage Theater an der Elbe", 53.5397, 9.9746),
    "operettenhaus": ("Stage Operettenhaus", 53.5495, 9.9671),
    "neue flora": ("Stage Theater Neue Flora", 53.5615, 9.9533),
    "theater des westens": ("Stage Theater des Westens", 52.5054, 13.3326),
    "bluemax": ("Stage Bluemax Theater", 52.5096, 13.3727),
    "apollo": ("Stage Apollo Theater", 48.7861, 9.2274),
    "palladium": ("Stage Palladium Theater", 48.7867, 9.2295),
    "metronom": ("Stage Metronom Theater", 51.4889, 6.8809),
    "colosseum": ("Colosseum Theater Essen", 51.4521, 6.9966),
    "musical dome": ("Musical Dome Köln", 50.9428, 6.9617),
    "starlight express theater": ("Starlight Express Theater", 51.4789, 7.2229),
}
CITY_CENTER = {
    "Hamburg": (53.5503, 9.9920), "Berlin": (52.5200, 13.4050),
    "Stuttgart": (48.7758, 9.1829), "Munich": (48.1351, 11.5820),
    "Cologne": (50.9375, 6.9603), "Düsseldorf": (51.2277, 6.7735),
    "Oberhausen": (51.4963, 6.8638), "Essen": (51.4556, 7.0116),
    "Bochum": (51.4818, 7.2162),
}
TITLES = {  # German marketing title -> canonical Western title
    "die eiskönigin": "Frozen",
    "der könig der löwen": "The Lion King",
    "der teufel trägt prada": "The Devil Wears Prada",
    "tarzan": "Tarzan",
    "hercules": "Hercules",
    "tina turner": "TINA - The Tina Turner Musical",  # not bare "tina" — that wrongly caught "Bibi & Tina"
    "zurück in die zukunft": "Back to the Future: The Musical",
    "& julia": "& Juliet",
    "mj -": "MJ The Musical",
    "mamma mia": "Mamma Mia!",
    "moulin rouge": "Moulin Rouge! The Musical",
    "hamilton": "Hamilton",
    "aladdin": "Aladdin",
    "wicked": "Wicked",
    "starlight express": "Starlight Express",
}
SKIP = re.compile(r"backstage|angebote|gutschein|casting|archiv|hotel|fuehrung|barrierefrei|faq|service|presse|jobs|agb|datenschutz", re.I)

# ── Poster picking ──────────────────────────────────────────────────────────
# Stage pages embed MANY shows' images (nav + "more shows" carousel) — so just
# grabbing og:image or the first transform URL is wrong: og:image is often a .tif
# the browser CAN'T render, and the first transform is usually another show's
# keyvisual (every page led with Prada's, so 7 shows wrongly showed Prada's poster).
# The reliable per-show signal is the portrait poster the page renders for ITSELF:
#   …/transform/{uuid}/SEN-MS-…ShowOnly-{CODE}-900x1459px   (only the current show
# carries a "ShowOnly" image; other shows on the page use Keyvisual/Header/LinkAd).
TRANSFORM = re.compile(r"https://mediaportal\.stage-entertainment\.com/transform/[a-f0-9-]+/[^\"?\\\s]+")
# Site-wide assets that are never a show's own poster.
GENERIC = re.compile(r"startbanner|composingnavi|25jahre|wortmarke|[-_]icon|logo[-_]?quadrat|navi\d|kachel|"
                     r"theatervermietung|backstage|foyer|theater_saal|archiv_logo|familie\d", re.I)
WEBP = "?io=transform:fill,width:1200&format=webp"
# Last-resort code for the few shows that ship neither a ShowOnly poster nor a
# renderable og:image (their code can't be derived from a .tif filename).
CODE_BY_SLUG = {"mj-": "MJ", "bibi-tina": "WBT"}


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    return urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "ignore")


def canon(title):
    t = title.lower()
    for de, en in TITLES.items():
        if de in t:
            return en
    return title


def pick_image(html, slug):
    og_m = re.search(r'property="og:image" content="([^"]+)"', html)
    og = htmllib.unescape(og_m.group(1)) if og_m else None
    trs = list(dict.fromkeys(TRANSFORM.findall(html)))           # de-duped, in document order
    cand = [u for u in trs if not GENERIC.search(u)]

    # 1) the show's own portrait poster — unique to this page
    showonly = [u for u in cand if "showonly" in u.lower()]
    showonly.sort(key=lambda u: 0 if "900x1459" in u else 1)     # prefer the portrait crop
    if showonly:
        return showonly[0] + WEBP

    # 2) a directly-renderable og:image (jpg/png/webp) — but a .tif can't be shown
    if og and not og.lower().split("?")[0].endswith((".tif", ".tiff")):
        return og

    # 3) match this show's code (from the .tif og filename, else the slug map) against
    #    the transform images, so we never fall through to another show's keyvisual.
    code = None
    if og:
        m = re.search(r"([A-Za-z]{2,})", og.split("/")[-1].split("?")[0])
        code = m.group(1).upper() if m else None
    if not code:
        code = next((c for k, c in CODE_BY_SLUG.items() if k in slug), None)
    if code:
        coded = [u for u in cand if code in u.split("/")[-1].upper()]
        coded.sort(key=lambda u: 0 if re.search(r"header|theaterbild|keyvisual", u, re.I) else 1)
        if coded:
            return coded[0] + WEBP
    return None


def main():
    pages = {BASE + "/"}
    for c in CITY_SLUGS:
        pages.add(f"{BASE}/musicals-shows/musicals-in-{c}")  # city hubs (may 404)
    links = set()
    for p in sorted(pages):
        try:
            html = fetch(p)
        except Exception:
            continue
        for m in re.findall(r'href="(/musicals-shows/[a-z0-9-]+)"', html):
            slug = m.rstrip("/").split("/")[-1]
            if SKIP.search(m) or "/" in slug:
                continue
            if slug.startswith("musicals-in-") or slug.startswith("musicals-shows"):
                continue  # city hub pages, not shows
            city = next((v for k, v in CITY_SLUGS.items() if slug.endswith("-" + k)), None)
            if city:
                links.add((m, slug, city))
    print(f"{len(links)} show pages")

    shows = {}
    for path, slug, city in sorted(links):
        try:
            html = fetch(BASE + path)
        except Exception as e:  # noqa: BLE001
            print(f"  [skip] {slug}: {e}")
            continue
        tm = re.search(r'property="og:title" content="([^"]+)"', html) or re.search(r"<title>([^<]+)</title>", html)
        raw_title = htmllib.unescape(
            re.split(r"\s*[|–]\s*(?:Stage Entertainment|Musical|Tickets).*$", tm.group(1))[0].strip()) if tm else slug
        if re.match(r"^musicals\b", raw_title, re.I):
            continue  # city overview page, not a show
        image = pick_image(html, slug)
        text = html.lower()
        # the nav mentions EVERY theatre once — pick the most-mentioned one (>=2)
        counts = {k: text.count(k) for k in THEATRES}
        best = max(counts, key=lambda k: counts[k])
        if counts[best] >= 2:
            venue, lat, lng = THEATRES[best]
        else:
            venue = "Stage Entertainment " + city
            lat, lng = CITY_CENTER[city]
        title = canon(raw_title)
        sid = "stage-" + re.sub(r"[^a-z0-9]+", "-", slug).strip("-")
        shows[sid] = {
            "id": sid, "title": title, "type": "resident",
            "venue": venue, "city": city, "country": "Germany",
            "lat": lat, "lng": lng,
            "start_date": None, "end_date": None,
            "ticket_url": BASE + path,
            "image": image,
            "tour_name": None, "verified": True,
            "source": "stage-entertainment.de",
        }
        print(f"  {title[:34]:36s} @ {venue[:30]:32s} {city}")
        time.sleep(0.3)

    out = {"meta": {"source": "stage-entertainment.de", "count": len(shows)}, "shows": list(shows.values())}
    (DATA / "stage_de.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nWrote {len(shows)} shows -> data/stage_de.json")


if __name__ == "__main__":
    main()
