"""China ??source: 銝掃繚銝絲??撟踹 / Shanghai Culture Square (shcstheatre.com).

The big China ticketing walls (Damai 憭折漲, Maoyan ?怎) are anti-bot fortified
(x5secdata / sliding-puzzle), so we scrape at the venue level instead. Shanghai
Culture Square is the mainland's flagship musical house and exposes a clean JSON
calendar API behind its ASP.NET front end:

  POST /webapi.ashx?op=GetTBLEVENTListForCalendar   data: year, month
       -> data.tblprogram[]  (every dated event that month; many genres)
  POST /webapi.ashx?op=GettblprogramCache           data: id=I_PROGRAM_ID
       -> data.tblprogram[0] (authoritative genre, run dates, poster, venue, lang)

We sweep the next ~13 months, keep only programs whose detail genre is ?喃???(Musicals), and emit one record per program with its full run.  Work-origin
tagging (Broadway / French / Korean / Chinese original ?? is NOT decided here ??build_shows.py resolves it via data/works.json, falling back to 銝剖??.

Output: data/china.json   Run: python scrapers/china.py

NB: shculturesquare.com (the old English domain) has lapsed and now serves an
unrelated Indonesian content farm ??do not use it.  The live site is shcstheatre.com.
"""

import json
import re
import sys
import io
import time
import urllib.request
import urllib.parse
from datetime import date
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

DATA = Path(__file__).resolve().parent.parent / "data"
BASE = "https://www.shcstheatre.com"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
HDR = {"User-Agent": UA, "Referer": BASE + "/Program/programList.aspx",
       "X-Requested-With": "XMLHttpRequest", "Content-Type": "application/x-www-form-urlencoded"}

# Shanghai Culture Square 銝絲??撟踹 ??憭銝剛楝597?? 暺策??(WGS84; same Google-
# geocoded coord as data/cn_venues.json, which is GCJ-02?GS-84 corrected for the
# OSM/Leaflet basemap).
VENUE = "銝絲??撟踹 Shanghai Culture Square"
LAT, LNG = 31.212666, 121.458089
MONTHS_AHEAD = 13


def api(op, **params):
    data = urllib.parse.urlencode(params).encode()
    req = urllib.request.Request(f"{BASE}/webapi.ashx?op={op}", data=data, headers=HDR)
    return json.loads(urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "ignore"))


def clean_title(briefname):
    """?喃??扼之?嗥?????憭抒??; 瘜祗???喃??扼??控隡舐?葉?? ???箇撅曹摩??"""
    m = re.search(r"??[^?+)??, briefname)
    t = m.group(1) if m else re.sub(r"^.*?訥銋?]??, "", briefname).strip()
    return re.sub(r"[嚗?]?銝剜??)嚗?$", "", t).strip()


def parse_run(cycle):
    """Parse the venue's run string. Handles full ranges ('2026.8.14-2026.8.30'),
    year-less ends ('2026.07.30 - 08.01' ??end inherits 2026, rolling to next year
    if it falls before the start), and single dates."""
    if not cycle:
        return None, None
    parts = re.split(r"\s*[-?]\s*", cycle.strip())

    def ymd(p):  # -> (y|None, m, d) ; None year when the part omits it
        m = re.match(r"(?:(\d{4})[.\-/])?(\d{1,2})[.\-/](\d{1,2})$", p.strip())
        return (int(m.group(1)) if m.group(1) else None, int(m.group(2)), int(m.group(3))) if m else None

    s = ymd(parts[0])
    if not s or s[0] is None:
        return None, None
    start = f"{s[0]}-{s[1]:02d}-{s[2]:02d}"
    if len(parts) < 2:
        return start, start
    e = ymd(parts[-1])
    if not e:
        return start, start
    ey = e[0] or s[0]
    if e[0] is None and (e[1], e[2]) < (s[1], s[2]):   # year-less end before start ??next year
        ey += 1
    return start, f"{ey}-{e[1]:02d}-{e[2]:02d}"


def collect_program_ids():
    """Sweep the calendar; return program_ids whose listing title looks like a musical."""
    ids = {}
    y, m = date.today().year, date.today().month
    for _ in range(MONTHS_AHEAD):
        try:
            j = api("GetTBLEVENTListForCalendar", year=str(y), month=f"{m:02d}")
        except Exception as e:  # noqa: BLE001
            print(f"  [skip] {y}-{m:02d}: {e}")
        else:
            for ev in j.get("data", {}).get("tblprogram", []):
                if "?喃??? in ev["SCS_WEB_BRIEFNAME"] or "?單??? in ev["SCS_WEB_BRIEFNAME"]:
                    ids.setdefault(ev["I_PROGRAM_ID"], ev["SCS_WEB_BRIEFNAME"])
        m += 1
        if m > 12:
            m, y = 1, y + 1
        time.sleep(0.2)
    return ids


def main():
    ids = collect_program_ids()
    print(f"{len(ids)} candidate musical program(s)")
    shows = {}
    for pid in ids:
        try:
            j = api("GettblprogramCache", id=str(pid))
            p = j["data"]["tblprogram"][0]
        except Exception as e:  # noqa: BLE001
            print(f"  [skip] {pid}: {e}")
            continue
        # authoritative genre check ??drop anything the venue doesn't file as a musical
        if "?喃??? not in (p.get("SCS_PERFORMANCE_TYPENAME") or "") and \
           "musical" not in (p.get("SCS_PERFORMANCE_TYPENAME_EN") or "").lower():
            continue
        title = clean_title(p["SCS_WEB_BRIEFNAME"])
        start, end = parse_run(p.get("SCS_WEBPERCYCLE"))
        pic = p.get("SCS_PC_YMXQ_PIC")
        image = (j.get("ImgBaseUrl", "") + pic) if pic else None
        sid = f"shcs-{pid}"
        shows[sid] = {
            "id": sid, "title": title, "type": "limited",
            "venue": VENUE, "city": "Shanghai", "city_cn": "上海", "country": "China",
            "lat": LAT, "lng": LNG,
            "start_date": start, "end_date": end,
            "ticket_url": f"{BASE}/Program/ProgramDetails.aspx?program_id={pid}",
            "image": image, "tour_name": None, "verified": True,
            "source": "shcstheatre.com",
        }
        print(f"  {title[:24]:26s} {start} ~ {end}  img={'Y' if image else '-'}")
        time.sleep(0.2)

    out = {"meta": {"source": "shcstheatre.com", "count": len(shows)}, "shows": list(shows.values())}
    (DATA / "china.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nWrote {len(shows)} shows -> data/china.json")


if __name__ == "__main__":
    main()
