"""Taiwan musicals from the utiki ticketing engine (寬宏售票 KHAM + udn售票 UDN + tixFun).

The sites run the same ASP.NET "UTK" engine on different skins:
  - listing page lists product ids + titles (KHAM: category 音樂劇=80; UDN: name search 音樂劇;
    tixFun: category 音樂劇=80, flat routes without the /application/UTK02 prefix)
  - a per-product session page carries the real run dates + venue (the marketing
    detail page body is polluted with refund boilerplate / cross-sell, so we ignore it)

KHAM session page  UTK02/UTK0201_00.aspx  -> an eventTABLE, one <tr> per session:
    <td>2026/06/18(四)14:30</td> <td>…<span id="PLACE_NAME">國家戲劇院</span>… q=<address></td>
UDN  session page  UTK02/UTK0203_.aspx    -> a yd_orderShow block:
    演出日期：2026/11/20 ~ 2026/11/29   演出地點：臺北表演藝術中心 大劇院
tixFun detail page /UTK0201_?PRODUCT_ID=… -> inline `__dataP = [...]` JSON, one entry
    per session with PLACE_NAME / ADDRESS / START_DATETIME (the only structured venue
    source on that skin — the marketing body cross-sells other shows' venues).
    tixFun is udn售票網's rebrand; new programs list only there, so both skins stay.

A program may tour several venues -> we emit one show per distinct venue with that
venue's own date range. Coordinates are left to Google geocoding (geocode_google.py
reads data/shows.json venues); we only resolve the English city for dedup/geocode.

Output: data/utiki.json    Run: python scrapers/utiki.py
"""

import json
import re
import sys
import io
import html
import hashlib
import urllib.request
import urllib.parse
import http.cookiejar
from datetime import datetime, timezone, timedelta
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
DATA = Path(__file__).resolve().parent.parent / "data"
TW_TZ = timezone(timedelta(hours=8))
UA = {"User-Agent": "Mozilla/5.0 (MusicalMap)"}

# non-musicals that can ride the 音樂劇 category/search (user-flagged philosophy:
# choirs, concerts and workshops are not staged musicals). Substring match on title.
EXCLUDE = ["老闆", "陽春麵", "演唱會", "合唱", "工作坊", "交響音樂會"]

# Chinese city/county -> English, to align with curated tw_venues + opentix cities.
CITY_MAP = {
    "臺北": "Taipei", "台北": "Taipei", "新北": "New Taipei", "基隆": "Keelung",
    "桃園": "Taoyuan", "新竹": "Hsinchu", "苗栗": "Miaoli", "臺中": "Taichung", "台中": "Taichung",
    "彰化": "Changhua", "南投": "Nantou", "雲林": "Yunlin", "嘉義": "Chiayi",
    "臺南": "Tainan", "台南": "Tainan", "高雄": "Kaohsiung", "屏東": "Pingtung",
    "宜蘭": "Yilan", "花蓮": "Hualien", "臺東": "Taitung", "台東": "Taitung",
    "澎湖": "Penghu", "金門": "Kinmen", "連江": "Lienchiang", "馬祖": "Lienchiang",
}

# All three are the same utiki "UTK" ASP.NET engine on different skins. They differ
# in: where dates+venue live (card / a per-product session table / the detail page's
# performance schedule), and whether the listing is already musical-only.
SITES = [
    {
        "name": "kham", "source": "kham.com.tw",
        "base": "https://kham.com.tw/application", "seed": None, "keep_musical": False,
        "listing": "/UTK01/UTK0101_06.aspx?TYPE=1&CATEGORY=80",        # category 80 = 音樂劇
        "detail": "https://kham.com.tw/application/UTK02/UTK0201_.aspx?PRODUCT_ID={pid}",
        "session": "/UTK02/UTK0201_00.aspx?PRODUCT_ID={pid}",
        "parse_list": "span_title", "venue_from": "session",
    },
    {
        "name": "udn", "source": "tickets.udnfunlife.com",
        "base": "https://tickets.udnfunlife.com/application", "seed": None, "keep_musical": False,
        "listing": "/UTK01/UTK0101_06.aspx?searchProductName=%E9%9F%B3%E6%A8%82%E5%8A%87",
        "detail": "https://tickets.udnfunlife.com/application/UTK02/UTK0201_.aspx?PRODUCT_ID={pid}",
        "session": None, "parse_list": "udn_cards", "venue_from": "card",  # card has dates+venues
    },
    {
        "name": "mna", "source": "ticket.mna.com.tw",
        "base": "https://ticket.mna.com.tw", "seed": "https://ticket.mna.com.tw/",
        "keep_musical": True,                                          # category 77 mixes concerts in
        "listing": "/UTK0102_?TYPE=1&CATEGORY=77",                    # 77 = 音樂 (musicals live here)
        "detail": "https://ticket.mna.com.tw/UTK0201_?PRODUCT_ID={pid}",
        "session": None, "parse_list": "mna_cards", "venue_from": "detail",  # venue from schedule
    },
    {
        "name": "tixfun", "source": "tixfun.com",
        "base": "https://tixfun.com", "seed": None, "keep_musical": False,
        "listing": "/UTK0102_?TYPE=1&CATEGORY=80",                    # 80 = 音樂劇 (same as KHAM)
        "detail": "https://tixfun.com/UTK0201_?PRODUCT_ID={pid}",
        "session": None, "parse_list": "tixfun_cards", "venue_from": "dataP",
    },
]


OPENER = urllib.request.build_opener(
    urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))


def get(url, referer=None):
    h = dict(UA)
    if referer:
        h["Referer"] = referer
    req = urllib.request.Request(url, headers=h)
    with OPENER.open(req, timeout=30) as r:   # shared cookie jar (MNA needs a session cookie)
        return r.read().decode("utf-8", "ignore")


def city_of(*texts):
    """Longest Chinese city/county name found in any of the texts -> English."""
    blob = " ".join(t or "" for t in texts)
    best, best_en = "", ""
    for zh, en in CITY_MAP.items():
        if zh in blob and len(zh) >= len(best):
            best, best_en = zh, en
    return best_en


def split_title(raw, en_hint=""):
    raw = html.unescape(raw or "").strip()
    m = re.search(r"[《＜<](.+?)[》＞>]", raw)
    if m:
        zh = m.group(1).strip()
    else:
        zh = re.sub(r"^(倫敦|經典法文|百老匯|影集式|全本|魔幻|外百老匯)+", "", raw)
        zh = re.sub(r"音樂劇.*$", "", zh).strip() or raw
    en = en_hint.strip()
    if not en:
        em = re.search(r"([A-Za-z][A-Za-z0-9 ,.&'\-:!?]{2,})\s*$", raw)
        en = em.group(1).strip() if em else ""
    return zh, en


# ---------- listing parsers -> [{pid, title, dates, venues, ended}] ----------
def list_span_title(h):
    """KHAM: cards only carry title; dates+venue come from the session page."""
    out = []
    for m in re.finditer(r'PRODUCT_ID=([A-Za-z0-9]+)"[^>]*>.*?<span class="title">(.*?)</span>', h, re.S):
        out.append({"pid": m.group(1), "title": m.group(2), "dates": [], "venues": [], "ended": False})
    return out


def list_udn_cards(h):
    """UDN: each card already holds title, date range, venue(s) and sale status."""
    out = []
    for m in re.finditer(r"PRODUCT_ID=([A-Za-z0-9]+).*?yd_card-body'>(.*?)</a>", h, re.S):
        pid, body = m.group(1), html.unescape(m.group(2))
        cells = [c.strip() for c in re.sub(r"<[^>]+>", "|", body).split("|") if c.strip()]
        if not cells:
            continue
        di = next((i for i, c in enumerate(cells)
                   if re.search(r"\d{4}/\d{1,2}/\d{1,2}\s*[~～至]", c)), None)
        dates, venues = [], []
        if di is not None:
            dates = re.findall(r"\d{4}/\d{1,2}/\d{1,2}", cells[di])
            if di + 1 < len(cells):
                venues = [v.strip() for v in cells[di + 1].split(",") if v.strip()]
        out.append({"pid": pid, "title": cells[0], "dates": dates,
                    "venues": venues, "ended": "結束銷售" in body})
    return out


# ---------- session parsers: -> list of {venue, city, dates:[YYYY-MM-DD], en} ----------
def sess_kham_table(h):
    m = re.search(r'class="eventTABLE".*?</table>', h, re.S)
    if not m:
        return []
    by_venue = {}
    for tr in re.findall(r"<tr.*?</tr>", m.group(0), re.S):
        tr = html.unescape(tr)                       # &amp;q= -> &q=
        d = re.search(r"(\d{4})/(\d{1,2})/(\d{1,2})", tr)
        v = re.search(r'id="PLACE_NAME">([^<]+)<', tr)
        if not d or not v:
            continue
        venue = v.group(1).strip()
        addr_m = re.search(r"[?&]q=([^&\"]+)", tr)
        addr = urllib.parse.unquote(addr_m.group(1)) if addr_m else ""
        ymd = f"{int(d.group(1)):04d}-{int(d.group(2)):02d}-{int(d.group(3)):02d}"
        rec = by_venue.setdefault(venue, {"venue": venue, "addr": "", "dates": []})
        rec["dates"].append(ymd)
        if addr and not rec["addr"]:
            rec["addr"] = addr
    res = []
    for rec in by_venue.values():
        res.append({"venue": rec["venue"], "city": city_of(rec["addr"], rec["venue"]),
                    "dates": sorted(rec["dates"]), "en": ""})
    return res


def list_mna_cards(h):
    """MNA: category cards carry title + date range; venue is on the detail page.
    The category mixes concerts in, so callers keep only 音樂劇 titles."""
    out = []
    for m in re.finditer(r'PRODUCT_ID=([A-Za-z0-9]+)".*?<h2>(.*?)</h2>.*?<h1[^>]*>(.*?)</h1>', h, re.S):
        title = html.unescape(re.sub(r"<[^>]+>", "", m.group(3))).strip()
        out.append({"pid": m.group(1), "title": title,
                    "dates": re.findall(r"\d{4}/\d{1,2}/\d{1,2}", m.group(2)),
                    "venues": [], "ended": False})
    return out


def list_tixfun_cards(h):
    """tixFun: cards (hero slides + grid) carry entity-encoded title + overall date
    range; venue/per-venue dates come from the detail page's __dataP JSON. A product
    can appear both as a slide and a grid card -> dedupe by pid."""
    out, seen = [], set()
    for m in re.finditer(
            r'href="/UTK0201_\?PRODUCT_ID=([A-Za-z0-9]+)"[^>]*class="[^"]*card[^"]*"(.*?)</a>',
            h, re.S):
        pid, body = m.group(1), html.unescape(m.group(2))
        if pid in seen:
            continue
        t = re.search(r"<h4>(.*?)</h4>", body, re.S)
        if not t:
            continue
        seen.add(pid)
        out.append({"pid": pid, "title": re.sub(r"<[^>]+>", "", t.group(1)).strip(),
                    "dates": re.findall(r"\d{4}/\d{1,2}/\d{1,2}", body),
                    "venues": [], "ended": False})
    return out


def sess_dataP(detail_html):
    """tixFun detail page embeds `__dataP = [...]` — one JSON entry per session with
    PLACE_NAME / ADDRESS / START_DATETIME. Group sessions by venue, city from the
    venue's street address (the marketing body is NOT safe: it cross-sells other
    programs' venues, so this JSON is the only venue source we trust on this skin)."""
    m = re.search(r"__dataP\s*=\s*(\[.*?\]);", detail_html, re.S)
    if not m:
        return []
    try:
        sessions = json.loads(m.group(1))
    except ValueError:
        return []
    by_venue = {}
    for s in sessions:
        venue = (s.get("PLACE_NAME") or "").strip()
        start = (s.get("START_DATETIME") or "")[:10]        # 2026-09-05T14:00:00
        if not venue or not re.match(r"\d{4}-\d{2}-\d{2}$", start):
            continue
        rec = by_venue.setdefault(venue, {"venue": venue, "addr": "", "dates": []})
        rec["dates"].append(start)
        if not rec["addr"]:
            rec["addr"] = s.get("ADDRESS") or ""
    return [{"venue": r["venue"], "city": city_of(r["addr"], r["venue"]),
             "dates": sorted(set(r["dates"])), "en": ""} for r in by_venue.values()]


def mna_venue(detail_html):
    """MNA detail page lists each session as 'date (day) HH:MM 場館'; take the venue
    that appears most across the schedule. The schedule rows give the base venue
    (臺中國家歌劇院); the description names the specific hall (…大劇院) — append it so
    we don't lose which of the 大/中/小 halls it is."""
    txt = re.sub(r"<[^>]+>", " ", detail_html)
    vens = [re.sub(r"\s", "", v) for v in re.findall(
        r"\d{1,2}:\d{2}\s*([一-鿿].{1,20}?(?:戲劇院|音樂廳|演藝廳|文化中心|歌劇院|巨蛋|表演廳|劇場|大會堂|中心))", txt)]
    if not vens:
        return ""
    from collections import Counter
    base = Counter(vens).most_common(1)[0][0]
    hall = re.search(re.escape(base) + r"(大劇院|中劇院|小劇場|實驗劇場|演奏廳|演藝廳|音樂廳|表演廳)",
                     re.sub(r"\s", "", txt))
    return base + hall.group(1) if hall else base


def ymd(s):
    """'2026/7/9' -> '2026-07-09'."""
    return "{:04d}-{:02d}-{:02d}".format(*[int(x) for x in s.split("/")])


def find_image(listing_html, pid):
    """Poster URL for a product — all three skins serve it from imgs2.utiki.com.tw
    with the PRODUCT_ID in the filename (…/{PID}.JPG, …_RWD.JPG, …_Product.JPG).
    Prefer the product-image folder (UTK2401) over og/thumbnail fallbacks that 404."""
    cands = re.findall(r"https://imgs2\.utiki\.com\.tw/Data/[^\"'() ]*" + re.escape(pid)
                       + r"[^\"'() ]*\.(?:JPG|jpg|png|PNG)", listing_html)
    if not cands:
        return None
    best = next((c for c in cands if "UTK2401" in c), cands[0])
    return best.split("?")[0]


PARSERS_LIST = {"span_title": list_span_title, "udn_cards": list_udn_cards,
                "mna_cards": list_mna_cards, "tixfun_cards": list_tixfun_cards}
PARSERS_SESS = {"kham_table": sess_kham_table}


def resolve_venues(site, p):
    """Return [{venue, city, dates:[YYYY-MM-DD]}] for a product, using whichever
    source carries the venue for this site (listing card / session table / detail)."""
    vf = site["venue_from"]
    if vf == "card":                                 # UDN: card already had venues
        rng = sorted({ymd(d) for d in p["dates"]})
        return [{"venue": v, "city": city_of(v), "dates": rng} for v in p["venues"]]
    if vf == "session":                              # KHAM: per-venue rows on session page
        try:
            sess = get(site["base"] + site["session"].format(pid=p["pid"]),
                       referer=site["detail"].format(pid=p["pid"]))
        except Exception:
            return []
        return PARSERS_SESS["kham_table"](sess)
    if vf == "dataP":                                # tixFun: per-session JSON on detail page
        try:
            detail = get(site["detail"].format(pid=p["pid"]),
                         referer=site["base"] + site["listing"])
        except Exception:
            return []
        return sess_dataP(detail)
    if vf == "detail":                               # MNA: dates on card, venue on detail page
        if not p["dates"]:
            return []
        try:
            detail = get(site["detail"].format(pid=p["pid"]),
                         referer=site["base"] + site["listing"])
        except Exception:
            return []
        venue = mna_venue(detail)
        if not venue:
            return []
        rng = sorted({ymd(d) for d in p["dates"]})
        return [{"venue": venue, "city": city_of(venue), "dates": rng}]
    return []


def main():
    today = datetime.now(TW_TZ).strftime("%Y-%m-%d")
    shows, dropped = [], []
    for site in SITES:
        try:
            if site.get("seed"):
                get(site["seed"])                    # seed the session cookie (MNA)
            listing = get(site["base"] + site["listing"])
        except Exception as e:
            print(f"  {site['name']}: listing failed ({e})", flush=True)
            continue
        products = PARSERS_LIST[site["parse_list"]](listing)
        # some listings (MNA category 77) mix concerts in — keep only 音樂劇 titles
        if site.get("keep_musical"):
            products = [p for p in products if "音樂劇" in p["title"]]
        print(f"  {site['name']}: {len(products)} 音樂劇 product(s)", flush=True)
        for p in products:
            raw_title = p["title"]
            if any(x in raw_title for x in EXCLUDE):
                dropped.append(raw_title + " (排除)"); continue
            zh, en = split_title(raw_title)
            img = find_image(listing, p["pid"])
            for v in resolve_venues(site, p):
                dates = v.get("dates") or []
                if not dates:
                    dropped.append(zh + f" @ {v['venue']} (無日期)"); continue
                start, end = dates[0], dates[-1]
                if end < today or p.get("ended"):
                    dropped.append(zh + f" @ {v['venue']} (已結束)"); continue
                shows.append({
                    "id": f"{site['name']}-{p['pid']}-{hashlib.md5(v['venue'].encode()).hexdigest()[:4]}",
                    "title": zh, "title_en": en,
                    "venue": v["venue"], "city": v["city"], "country": "Taiwan",
                    "lat": None, "lng": None,        # filled by geocode_google.py
                    "start_date": start, "end_date": end,
                    "image": img,
                    "ticket_url": site["detail"].format(pid=p["pid"]),
                    "type": "tour", "verified": True, "source": site["source"],
                })
    out = {"meta": {"source": "utiki (kham+udn+mna+tixfun)", "count": len(shows)}, "shows": shows}
    (DATA / "utiki.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(shows)} -> data/utiki.json", flush=True)
    for s in shows:
        print(f"    keep: {s['title']} @ {s['venue']} ({s['city']}) {s['start_date']}~{s['end_date']}", flush=True)
    for d in dropped:
        print("    drop:", d, flush=True)


if __name__ == "__main__":
    main()
