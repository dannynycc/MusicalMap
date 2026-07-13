"""Global musicals via the Ticketmaster Discovery API.

⚠️ REQUIRES A FREE API KEY — set env var TICKETMASTER_API_KEY.
   Get one at https://developer.ticketmaster.com (register an app → Consumer Key).
   Without the key every endpoint returns 401, so this scraper is UNTESTED until
   a key is supplied; once it is, run it and verify the output before trusting it.

Covers countries the other scrapers miss (Australia, NZ, much of Europe, etc.).
Ticketmaster returns one event per performance date, so we aggregate events that
share a show + venue into a single run (min start date → max end date).

Output: data/ticketmaster.json   Run: TICKETMASTER_API_KEY=xxx python scrapers/ticketmaster.py
"""

import json
import os
import re
import sys
import io
import time
import urllib.request
import urllib.parse
import urllib.error
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

DATA = Path(__file__).resolve().parent.parent / "data"
API = "https://app.ticketmaster.com/discovery/v2/events.json"
_KEYFILE = Path(__file__).resolve().parent / ".tm_key"   # gitignored local key
KEY = os.environ.get("TICKETMASTER_API_KEY") or (
    _KEYFILE.read_text(encoding="utf-8").strip() if _KEYFILE.exists() else None)
# One Discovery API spans every national Ticketmaster site; we sweep each market
# by ISO country code. Dedupe is by (show, venue) so the same production showing
# up under multiple country sites collapses into one record (collecting each
# region's ticket link). Extend this list to widen coverage.
# Only sweep countries the curated sources DON'T cover (US/UK/JP/DE/ES/FR/MX/NL
# are already covered and dropped at build anyway). Smaller volumes here let us
# fetch ALL pages, so end_date = the real last scheduled performance.
# GB included: London is curated (londontheatre.co.uk) but the UK REGIONAL
# touring circuit (Manchester/Glasgow/…) isn't — build keeps TM GB records for
# non-London cities only. (Lesson from missing the Miss Saigon UK tour.)
# US included not for new markers (Broadway/tours are curated) but so build can
# ATTACH Ticketmaster purchase links to existing records (link enrichment).
# Global deep sweep: every market the Ticketmaster Discovery API serves. Empty /
# unsupported codes just return nothing and are skipped — dedupe by (show, venue)
# collapses a production appearing under several national sites. Curated-source
# countries (US/GB/…) stay in for ticket-link enrichment of existing records.
COUNTRIES = [
    # North America
    "US", "CA", "MX",
    # Oceania
    "AU", "NZ",
    # UK & Ireland
    "GB", "IE",
    # Western / Central / Northern / Southern / Eastern Europe
    "AT", "BE", "CH", "CZ", "DE", "DK", "ES", "FI", "FR", "GR", "HU",
    "IT", "LU", "NL", "NO", "PL", "PT", "RO", "SE", "SK", "HR", "SI",
    "EE", "LV", "LT", "BG",
    # Middle East / Africa
    "AE", "IL", "TR", "ZA",
    # Asia-Pacific
    "SG",
]


def tm_search(title, ref_url):
    """Stable fallback when an event has no attraction page: a Ticketmaster search
    page for the title, on the same national domain as the event (so a UK event
    keeps .co.uk). Never returns an expiring /event/ URL."""
    host = "www.ticketmaster.com"
    m = re.match(r"https?://([^/]+)", ref_url or "")
    if m:
        host = m.group(1)
    return f"https://{host}/search?q=" + urllib.parse.quote(title)


def clean_title(t):
    """Normalize the noisy event names Ticketmaster uses so the same production
    collapses to one record (accessibility/preview performances, region tags,
    promoter prefixes, ALL-CAPS)."""
    t = (t or "").strip()
    if re.search(r"do not purchase|test event", t, re.I):
        return ""  # junk/test listings
    # 一般「機構 presents 劇名」前綴(The Lexington Theatre Co. presents Matilda 等):
    # presents 前面含機構詞才剝,避免誤傷劇名本身含 presents 的罕見情況(2026-07-13)。
    # 必須在 disney 前綴規則之前跑:「Picayune Theatre Company Presents Disney's Frozen」
    # 剝完機構後才輪得到 disney's 規則。
    m = re.match(r"^(.{3,60}?)\s+presents?\s+(.+)$", t, flags=re.I)
    if m and re.search(r"theat(?:re|er)|company|\bco\b|productions?|players|opera|society|"
                       r"guild|stage|academy|arts|university|college|school|series",
                       m.group(1), flags=re.I):
        t = m.group(2).strip()
    # promoter prefixes
    t = re.sub(r"^(disney\s+presents\s+|disney'?s\s+|cameron\s+mackintosh'?s\s+)", "", t, flags=re.I)
    # region / version parenthetical anywhere, e.g. "(Australia)", "(UK)", "(Touring)"
    t = re.sub(r"\s*\((?:australia|uk|us|usa|touring|broadway|the\s+musical)\)", "", t, flags=re.I)
    # accessibility / performance-type qualifiers after a dash (drop to end)
    t = re.sub(
        r"\s*[-–]\s*(auslan|audio[- ]?desc|relaxed|opening night|night with|previews?|"
        r"captioned|matinee|sensory|signed|the broadway musical|the musical|broadway)\b.*$",
        "", t, flags=re.I)
    # trailing accessibility words without a dash
    t = re.sub(r"\s+(relaxed performance|captioned.*|audio desc.*)$", "", t, flags=re.I)
    # bare trailing "the musical" / "the broadway musical"(無 dash 型,2026-07-13)
    t = re.sub(r"\s*(?:[-–:]\s*)?the\s+(?:broadway\s+)?musical$", "", t, flags=re.I)
    t = t.strip(" -–:")
    if len(t) > 4 and t.isupper():       # de-shout ALL-CAPS titles
        t = t.title()
    return t


def display_name(t):
    """Lighter clean than clean_title: keep the production's distinguishing
    descriptors — "(Australia)", "The Broadway Musical" — so the card can show the
    faithful production name, but drop per-performance noise (accessibility/preview
    tags, ALL-CAPS shouting, trailing "Tickets"). Returns "" for junk."""
    t = (t or "").strip()
    if re.search(r"do not purchase|test event", t, re.I):
        return ""
    t = re.sub(r"^(disney\s+presents\s+|disney'?s\s+|cameron\s+mackintosh'?s\s+)", "", t, flags=re.I)
    t = re.sub(r"\s*[-–]\s*(auslan|audio[- ]?desc\w*|relaxed|opening night|night with|"
               r"previews?|captioned|matinee|sensory|signed)\b.*$", "", t, flags=re.I)
    t = re.sub(r"\s+(relaxed performance|captioned.*|audio desc.*)$", "", t, flags=re.I)
    t = re.sub(r"\s*[-–:]?\s*tickets?$", "", t, flags=re.I)        # trailing "Tickets"
    t = t.strip(" -–:")
    if len(t) > 4 and t.isupper():
        t = t.title()
    return t


def fetch(params):
    url = API + "?" + urllib.parse.urlencode(params)
    for attempt in range(4):
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and attempt < 3:
                time.sleep(1.5 * (attempt + 1))   # transient server/rate hiccup → back off
                continue
            raise
    return {}   # unreachable (loop returns or raises), but keeps the type checker happy


# Ticketmaster Discovery caps deep paging at 1000 items (page*size); requesting
# beyond that returns HTTP 400. With size=100 the last valid page is 9. Big
# TM caps deep paging at 1000 items per query. 舊法=全國掃前 1000 筆(date asc)+大城市
# 清單補洞——但非大城的遠期場次永遠掉在窗外(2026-07-13 使用者抓到 Lexington 的
# Matilda 7/30 場漏抓:US 單月 musical events 1,400~2,200 筆,7 月中掃到月底就爆窗)。
# 治本=自適應時間分片:窗內量 >SPLIT_AT 就對半切,遞迴到每片 ≤SPLIT_AT 再整片抓,
# 未來量怎麼長都扛得住;城市補丁清單退役。
MAX_PAGE = 9
SPLIT_AT = 900          # ≤900 整片抓(100×10 頁上限內留 buffer)
SWEEP_MONTHS = 13      # 掃描地平線:今天起 13 個月(涵蓋隔年同月)
MIN_SLICE_DAYS = 2     # 分片下限,防病態遞迴


def _window_total(cc, start, end):
    """One cheap probe: how many musical events in [start, end)?"""
    data = fetch({
        "apikey": KEY, "classificationName": "Musical", "segmentName": "Arts & Theatre",
        "countryCode": cc, "size": 1,
        "startDateTime": start.strftime("%Y-%m-%dT00:00:00Z"),
        "endDateTime": end.strftime("%Y-%m-%dT00:00:00Z"),
    })
    return (data.get("page") or {}).get("totalElements") or 0


def _sweep_window(cc, start, end):
    """Yield every musical event in [start, end), splitting the window in half
    whenever it holds more than SPLIT_AT events (adaptive bisection)."""
    total = _window_total(cc, start, end)
    time.sleep(0.2)
    if total > SPLIT_AT and (end - start).days > MIN_SLICE_DAYS:
        mid = start + (end - start) / 2
        yield from _sweep_window(cc, start, mid)
        yield from _sweep_window(cc, mid, end)
        return
    page = 0
    while page <= MAX_PAGE:
        params = {
            "apikey": KEY, "classificationName": "Musical", "segmentName": "Arts & Theatre",
            "countryCode": cc, "size": 100, "page": page, "sort": "date,asc",
            "startDateTime": start.strftime("%Y-%m-%dT00:00:00Z"),
            "endDateTime": end.strftime("%Y-%m-%dT00:00:00Z"),
        }
        try:
            data = fetch(params)
        except urllib.error.HTTPError as e:
            if e.code == 400:    # past the deep-paging ceiling → stop, keep what we have
                break
            raise
        for ev in data.get("_embedded", {}).get("events", []):
            yield ev
        info = data.get("page", {})
        page += 1
        if page >= info.get("totalPages", 0):
            break
        time.sleep(0.2)


def sweep_country(cc):
    """Adaptive time-sliced sweep over the whole horizon (today → +SWEEP_MONTHS)."""
    from datetime import datetime, timedelta
    start = datetime.utcnow() - timedelta(days=1)   # 含今天(UTC 邊界緩衝)
    end = start + timedelta(days=SWEEP_MONTHS * 31)
    yield from _sweep_window(cc, start, end)


def main():
    if not KEY:
        print("✗ TICKETMASTER_API_KEY not set — get a free key at "
              "https://developer.ticketmaster.com and re-run. (no output written)")
        return

    runs = {}  # (show, venue) -> aggregated record

    def add_event(ev, cc):
        cl = (ev.get("classifications") or [{}])[0]
        genre = ((cl.get("genre") or {}).get("name") or "").lower()
        sub = ((cl.get("subGenre") or {}).get("name") or "").lower()
        seg = ((cl.get("segment") or {}).get("name") or "").lower()
        if seg != "arts & theatre" or "musical" not in (genre + " " + sub):
            return                                    # keep only genuine musicals
        # skip events TM marks cancelled/postponed — their pages 404 / "event canceled"
        status = ((ev.get("dates", {}).get("status") or {}).get("code") or "").lower()
        if status in ("cancelled", "canceled", "postponed"):
            return
        v = (ev.get("_embedded", {}).get("venues") or [{}])[0]
        loc = v.get("location") or {}
        title = clean_title(ev.get("name") or "")
        venue = (v.get("name") or "").strip()
        date = (ev.get("dates", {}).get("start", {}) or {}).get("localDate")
        if not title or not venue or not loc.get("latitude"):
            return
        att = (ev.get("_embedded", {}).get("attractions") or [{}])[0]
        # Link to the STABLE attraction (show) page, e.g. .../funny-girl-tickets/artist/NNN
        # — NOT the per-performance /event/ URL, which 404s once that date passes. When
        # no attraction page exists, fall back to a (stable) search page, never /event/.
        link = att.get("url") or tm_search(title, ev.get("url"))
        # Faithful production name for the card: prefer the attraction (show) name,
        # keep its distinguishing descriptors; only set when it adds info beyond the
        # canonical title (e.g. "Anastasia - The Broadway Musical (Australia)").
        disp = display_name(att.get("name") or ev.get("name") or "")
        # attraction 名與(尚未英文化的)劇名零 token 重疊=呈現方/劇團名(「Lexington
        # Theatre Co.」對「Matilda」),不是製作名 → 不當 tour_name(2026-07-13:clean_title
        # 剝 presents 後 id 失去指紋,build_shows 端抓不到,必須在源頭擋)。此階段 title
        # 仍是事件原文,在地語言製作名(La Novicia Rebelde)與 title 同文必有交集,不誤傷。
        _tok = lambda x: set(re.findall(r"[a-z0-9]+", (x or "").lower())) - {
            "the", "a", "an", "of", "and", "le", "les", "la", "de", "musical", "on", "in"}
        tour = disp if disp and disp.lower() != title.lower() and (_tok(disp) & _tok(title)) else None
        key = (title.lower(), venue.lower())
        rec = runs.get(key)
        if not rec:
            imgs = sorted(ev.get("images", []), key=lambda i: -(i.get("width") or 0))
            runs[key] = {
                "id": "tm-" + re.sub(r"[^a-z0-9]+", "-", f"{title}-{venue}".lower()).strip("-"),
                "title": title, "type": "tour",  # TM runs are limited engagements / tour stops
                "venue": venue,
                "city": (v.get("city") or {}).get("name") or "",
                "country": (v.get("country") or {}).get("name") or cc,
                "lat": round(float(loc["latitude"]), 6),
                "lng": round(float(loc["longitude"]), 6),
                "start_date": date, "end_date": date,
                "ticket_url": link,
                "attraction_url": att.get("url"),
                "ticket_links": ([{"country": cc, "url": link}] if link else []),
                "image": imgs[0]["url"] if imgs else None,
                "tour_name": tour, "verified": True,
                "source": "ticketmaster",
            }
        else:  # widen the run's date range + collect this region's link
            if date and (not rec["start_date"] or date < rec["start_date"]):
                rec["start_date"] = date
            if date and (not rec["end_date"] or date > rec["end_date"]):
                rec["end_date"] = date
            if link and not any(l["country"] == cc for l in rec["ticket_links"]):
                rec["ticket_links"].append({"country": cc, "url": link})

    for cc in COUNTRIES:
        try:
            for ev in sweep_country(cc):   # adaptive time-sliced full sweep(舊城市補丁退役)
                add_event(ev, cc)
            print(f"  {cc}: {len(runs)} cumulative runs")
        except Exception as e:  # noqa: BLE001
            print(f"  [{cc}] failed: {e}")

    # NOTE: start_date is the earliest *available* performance (the API drops
    # expired dates), end_date the last scheduled performance. We keep them as-is
    # (no faking) — for a "what's playing on date X" view, the real available
    # window is the honest answer. onsale_only flags that these are availability
    # dates, not a confirmed opening→closing run, so the UI can label them right.
    for r in runs.values():
        r["onsale_only"] = True

    shows = list(runs.values())
    out = {"meta": {"source": "ticketmaster", "count": len(shows)}, "shows": shows}
    (DATA / "ticketmaster.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nWrote {len(shows)} runs -> data/ticketmaster.json")


if __name__ == "__main__":
    main()
