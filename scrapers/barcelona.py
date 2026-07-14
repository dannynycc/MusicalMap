"""Barcelona musicals — source: teatrebarcelona.com (same WordPress platform as
teatromadrid.com; Catalan/Spanish). Listing items carry title, venue, run dates
(dd/mm/yyyy), poster and a /espectacle/ detail link. Catalan/Spanish marketing
titles are mapped to canonical worldwide titles so they merge with the same show
elsewhere; the local title is kept as tour_name so the popup shows it.

Output: data/barcelona.json   Run: python scrapers/barcelona.py
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
PAGE = ("https://www.teatrebarcelona.com/cartellera-teatre-barcelona/pagina/{n}"
        "?sort=popular&genre_id=8&location=Barcelona")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) MusicalMap/0.1"

# Catalan/Spanish marketing title -> canonical worldwide title (accent-less lowercase)
TITLES_ES = {
    "los miserables": "Les Misérables", "els miserables": "Les Misérables",
    "el rey leon": "The Lion King", "el rei lleo": "The Lion King",
    "cenicienta": "Cinderella", "la ventafocs": "Cinderella",
    "sonrisas y lagrimas": "The Sound of Music",
    "six": "SIX", "wicked": "Wicked",
    "la sirenita": "The Little Mermaid", "la sireneta": "The Little Mermaid",
    "mamma mia": "Mamma Mia!",
    "el fantasma de la opera": "The Phantom of the Opera",
    "el fantasma de l'opera": "The Phantom of the Opera",
    "la bella y la bestia": "Beauty and the Beast",
    "la bella i la bestia": "Beauty and the Beast",
    "aladdin": "Aladdin", "aladi": "Aladdin",
    "matilda": "Matilda The Musical", "grease": "Grease", "chicago": "Chicago",
    "el medico": "El Médico (The Physician)",
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
    if not m:
        return None
    # 年份 sanity(madrid.py 同款;整頁掃日期會撈到雜訊怪年,2026-07-14)
    if not (2000 <= int(m.group(3)) <= 2035):
        return None
    return f"{m.group(3)}-{m.group(2)}-{m.group(1)}"


def detail_dates(url):
    """列表項常只印一個日期(週末親子劇的零星場次尤其),導致 end 缺 → 圖卡日期空白。
    詳情頁列出全部場次(dd/mm/yyyy),抓回來取 min/max 當起迄(2026-07-09 資料品質稽核:
    No me toques el cuento 列表只有 2025-01-18,詳情頁實有 2026/04-05 場次)。"""
    try:
        page = fetch(url)
    except Exception:  # noqa: BLE001
        return []
    return sorted({iso(x) for x in re.findall(r"\d{2}/\d{2}/\d{4}", page) if iso(x)})


def main():
    shows = {}
    for n in range(1, 8):
        try:
            html = fetch(PAGE.format(n=n))
        except Exception as e:  # noqa: BLE001
            print(f"  [page {n}] {e}")
            break
        items = re.findall(r'<div class="funcion-item-list[^"]*">(.*?)'
                           r'(?=<div class="funcion-item-list|<div class="paginat|$)', html, re.S)
        if not items:
            break
        page_added = 0
        for it in items:
            dt = re.search(r'data-title="([^"]+)"', it)
            href = re.search(r'href="(https://www\.teatrebarcelona\.com/espectacle/[^"]+?)(?:\?[^"]*)?"', it)
            if not dt or not href:
                continue
            raw = htmllib.unescape(dt.group(1))
            parts = re.split(r"\s*(?:→|→)\s*", raw)
            title_es = parts[0].strip()
            venue = (parts[1].strip() if len(parts) > 1 else "")
            dates = re.findall(r"(\d{2}/\d{2}/\d{4})", re.sub(r"<[^>]+>", " ", it))
            start = iso(dates[0]) if dates else None
            end = iso(dates[1]) if len(dates) > 1 else None
            if not end:   # 列表只給一個(或零個)日期 → 進詳情頁補完整檔期
                dd = [x for x in detail_dates(href.group(1)) if not start or x >= start]
                if dd:
                    start = start or dd[0]
                    end = dd[-1]
            img = re.search(r'(?:data-src|src)="(https://www\.teatrebarcelona\.com/[^"]+\.(?:jpg|jpeg|png|webp))"', it)
            title = canon(title_es)
            if "por confirmar" in venue.lower() or "confirmar" in venue.lower():
                continue
            lat, lng = geocode(f"{deaccent(venue)}|barcelona", f"{venue}, Barcelona, Spain")
            if lat is None:
                continue  # precision over volume
            sid = "bcn-" + re.sub(r"[^a-z0-9]+", "-", href.group(1).split("/espectacle/")[1].lower()).strip("-")
            shows[sid] = {
                "id": sid, "title": title, "type": "tour",
                "venue": venue or "Barcelona", "city": "Barcelona", "country": "Spain",
                "lat": lat, "lng": lng,
                "start_date": start, "end_date": end,
                "ticket_url": href.group(1),
                "image": img.group(1) if img else None,
                "tour_name": title_es,  # local Catalan/Spanish production name
                "verified": True, "source": "teatrebarcelona.com",
            }
            page_added += 1
            print(f"  {title_es[:30]:32s} -> {title[:24]:26s} @ {venue[:24]:26s} {start}~{end}")
        if page_added == 0:
            break

    out = {"meta": {"source": "teatrebarcelona.com", "count": len(shows)}, "shows": list(shows.values())}
    (DATA / "barcelona.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nWrote {len(shows)} shows -> data/barcelona.json")


if __name__ == "__main__":
    main()
