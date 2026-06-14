"""Merge all per-source data files into data/shows.json (what the frontend reads).

Each source file is {"meta": {...}, "shows": [...]}. We concatenate, de-dup by
id (last source wins), and stamp combined meta. Keeping sources separate means a
re-scrape of one source never clobbers the others.

Run:  python scrapers/build_shows.py
"""

import json
import re
import sys
import io
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

DATA = Path(__file__).resolve().parent.parent / "data"


def _norm(title):
    """Pure title normalisation (no registry): the canonical key so the same show
    titled differently across sources groups together (e.g. 'SIX' == 'SIX: The
    Musical', 'Mamma Mia!' == 'Mamma Mia', 'Les Misérables' == 'Les Miserables').
    Diacritics are stripped BEFORE the ascii filter, otherwise 'é' becomes a word
    break and spellings diverge."""
    t = re.sub(r"[–—]", "-", title or "")  # en/em-dash → '-' BEFORE ascii-strip drops them
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode()
    t = t.lower().strip()
    t = re.sub(r"^disney(?:'s| presents)\s+", "", t)   # strip BEFORE 'the' so
    t = re.sub(r"^the\s+", "", t)                       # "Disney's The Lion King" == "The Lion King"
    # any dash/colon marketing subtitle that mentions "musical", in any language
    # ("– Das Hit-Musical auf Schweizerdeutsch", ": The Broadway Musical", …)
    t = re.sub(r"\s*[:\-–—]\s*[^:]*musical.*$", "", t)
    t = re.sub(r"\s*[:\-–—]\s*(a\s+new\s+musical|the\s+musical|reimagined).*$", "", t)
    # trailing "the Xxx Yyy Musical" brand tails without a dash. The "the" is
    # REQUIRED — otherwise titles like "High School Musical" get over-stripped
    # to "high" (real bug: its group missed the official-site table entirely).
    t = re.sub(r"\s+the\s+(?:[\w'!\-]+\s+){0,4}musical$", "", t)
    t = re.sub(r"[^a-z0-9]+", " ", t).strip()
    if not t:  # ASCII-strip emptied it (CJK-only title, or a title that IS just
        # "…Musical"). Fall back to Unicode word chars so CJK titles keep a stable,
        # DISTINCT key — otherwise every Chinese-only show in a city collapses to ""
        # and gets merged into one (e.g. 萬世巨星 vs 史瑞克 both -> "").
        t = re.sub(r"[^\w]+", " ", title or "", flags=re.UNICODE).lower().strip()
    return t


# ─── Canonical works registry (data/works.json) ────────────────────────────────
# ONE source of truth for tradition tag + cross-language de-dup + bilingual display.
# Every alias/canonical is indexed by _norm() so any title a work appears under
# resolves to the same group, tradition, and English prefix. See works.json header.
def _load_works():
    path = DATA / "works.json"
    idx, trad_by_cgroup = {}, {}
    if not path.exists():
        return idx, trad_by_cgroup
    for w in json.loads(path.read_text(encoding="utf-8")).get("works", []):
        cgroup = _norm(w["canonical"])
        entry = {"canonical": w["canonical"], "tradition": w.get("tradition"), "cgroup": cgroup}
        trad_by_cgroup[cgroup] = w.get("tradition")
        for name in [w["canonical"], *w.get("aliases", [])]:
            idx[_norm(name)] = entry           # alias/canonical → canonical work
    return idx, trad_by_cgroup


WORK_IDX, TRADITION_BY_CGROUP = _load_works()


def group_key(title):
    """Registry-aware canonical group: normalise, then collapse any known alias to
    its canonical group (so 'Macskák' / 'キャッツ' / 'Cats' share one group)."""
    t = _norm(title)
    w = WORK_IDX.get(t)
    return w["cgroup"] if w else t


def resolve_work(title):
    """The registry entry a title belongs to (or None)."""
    return WORK_IDX.get(_norm(title))

# Curated sources (precise data). Order matters for de-dup: later files win.
SOURCE_FILES = ["broadway.json", "westend.json", "tours.json", "intl.json",
                "shiki.json", "takarazuka.json", "interpark.json",
                "atg.json", "stage_de.json", "madrid.json", "opentix.json",
                "utiki.json", "japan.json", "easteurope.json", "manual.json"]

# When several ticket sources list the SAME show in the SAME city, we keep one
# record (highest priority = most authoritative venue data) and attach every
# source's purchase link to the card. Lower index = higher priority.
SOURCE_PRIORITY = ["shiki.jp", "kageki", "broadway-show-tickets", "londontheatre",
                   "interpark", "stage-entertainment", "teatromadrid", "manual",
                   "broadway.org", "atgtickets", "ticketmaster"]
SOURCE_LABEL = {
    "broadway-show-tickets": "Broadway票務", "londontheatre": "LondonTheatre",
    "broadway.org": "Broadway.org", "shiki.jp": "四季官網", "kageki": "宝塚官網",
    "interpark": "Interpark", "atgtickets": "ATG", "stage-entertainment": "Stage官網",
    "ticketmaster": "Ticketmaster", "manual": "官方售票", "shgtheatre": "上海大劇院",
    "teatromadrid": "TeatroMadrid",
    "livenation": "Live Nation", "ndm.cz": "NDM官網",
}
# 官網(製作方/劇團/劇院自營) vs 售票平台(第三方票務)。
OFFICIAL_SOURCES = ("shiki.jp", "kageki", "stage-entertainment", "shgtheatre", "ndm.cz")


def src_kind(src):
    return "official" if any(k in (src or "") for k in OFFICIAL_SOURCES) else "ticketing"


def src_prio(src):
    for i, p in enumerate(SOURCE_PRIORITY):
        if p in (src or ""):
            return i
    return 99


def src_label(src):
    for k, v in SOURCE_LABEL.items():
        if k in (src or ""):
            return v
    return "售票連結"
# Ticketmaster is added only for countries the curated sources DON'T cover,
# so it fills global gaps (Australia, NZ, Ireland, Nordics, Canada…) without
# duplicating the well-curated US/UK/etc. productions.
TM_FILE = "ticketmaster.json"


def city_key(c):
    """'Boston, MA' == 'Boston' — state/region suffixes break dedup keys."""
    return (c or "").lower().split(",")[0].strip()


def venue_key(venue, city):
    """Stable key for venue-level coordinate corrections (data/venue_coords.json).
    Matches on lowered venue name + city (state suffix stripped)."""
    return f"{(venue or '').strip().lower()}|{city_key(city)}"


def country_norm(c):
    c = (c or "").lower()
    if "united states" in c or c == "usa":
        return "us"
    if "great britain" in c or "united kingdom" in c or c == "uk":
        return "gb"
    return c.strip()


# Some sources append admission notices to the show name, e.g.
# "Phantom Of The Opera (Entry requires a valid photo ID. Guests 13+ …)".
# Strip such notice-parentheticals (but keep real ones like
# "Two Strangers (Carry a Cake Across New York)").
NOTICE_RE = re.compile(
    r"\s*\([^)]*(require|must\b|guests?\b|valid|photo id|accompani|aged?\b|"
    r"recommended|running time|interval|approx|under \d|relaxed|auslan|captioned|"
    r"audio[- ]?desc|matinee|preview)[^)]*\)\s*", re.I)


# Trailing location/tour qualifier some sources append to disambiguate, e.g.
# Ticketmaster "Wicked (NY)" — it breaks grouping (→ a duplicate marker next to the
# already-listed New York run). Strip ONLY short location/tour qualifiers, never a
# real parenthetical like "Two Strangers (Carry a Cake Across New York)".
LOC_QUALIFIER_RE = re.compile(
    r"\s*\(\s*(?:[A-Za-z]{2}|N\.?Y\.?C?|NYC|U\.?K\.?|U\.?S\.?A?|"
    r"broadway|west\s*end|national(?:\s*tour)?|north\s*american(?:\s*tour)?|"
    r"u\.?s\.?\s*tour|uk\s*tour|on\s*tour|touring|"
    r"[A-Za-z][\w .'’&-]*,\s*[A-Za-z]{2})\s*\)\s*$", re.I)  # "(New York, NY)" / "(Cleveland, OH)"


def clean_title(t):
    t = (t or "").strip()
    t = re.sub(r"\s*\|.*$", "", t)          # drop promoter pipe-tails (… | Official … Packages)
    prev = None
    while prev != t:
        prev = t
        t = NOTICE_RE.sub(" ", t).strip()
        t = LOC_QUALIFIER_RE.sub("", t).strip()
    return re.sub(r"\s{2,}", " ", t).strip()


def bilingual(title):
    """Prepend the canonical English/original for registered works whose title here
    is in another language → 'Cats Macskák' / 'Jesus Christ Superstar 萬世巨星'.
    Local original works are unregistered and stay as-is."""
    w = resolve_work(title)
    if w and w["canonical"].lower() not in (title or "").lower():
        return f"{w['canonical']} {title}"
    return title


# Events that ticketmaster files under "Musical" but aren't staged musicals —
# film-screening tours, concert/tribute nights, comedy/book tours. Title-matched so
# it never touches a real show (e.g. "Hedwig and the Angry Inch" stays; only
# "...Hedwig 25th Anniversary Movie Tour" is dropped).
NOT_MUSICAL_RE = re.compile(
    r"\bmovie tour\b|\bfilm (?:tour|screening|concert)\b|\bscreening\b|"
    r"\bdocumentary\b|\bbook tour\b|\bcomedy (?:tour|special)\b|\bstand[- ]?up\b|"
    r"\bin conversation\b|\bspeaking tour\b|"
    r"\bcursed child\b|"                       # Harry Potter and the Cursed Child is a PLAY
    r"\bnanta\b|\bpainters\b|\bsleep no more\b|"   # KR non-verbal / immersive (no songs)
    r"martial arts performance|comic martial arts|"
    r"scotch college|"                            # school/amateur staging, not a public run
    r"a very musical theatre christmas|"          # Christmas cabaret revue, not a book musical
    # TM files tribute/concert/songbook/drag acts under "Musical" — they're not
    # book musicals. Verified against the data: drops only these, no real shows.
    r"\btribute\b|\bconcert\b|\bsoundtrack\b|\bgala\b|\bcelebration\b|"
    r"\bsymphony\b|\borchestra\b|\bthe (?:songs|music|hits) of\b|\bsongs of\b|"
    r"\bdrag (?:show|along|race|brunch|queen)\b|"
    r"\bnonstop\b|koncert", re.I)        # medley / gala-concert nights (EE 'koncert')

# ─── Tradition tags ──────────────────────────────────────────────────────────
# A show's tag is the WORK's ORIGIN tradition, not where it plays (Wicked in Seoul
# is still Broadway/West End; Elisabeth in Tokyo is still 德奧). Registered works
# (works.json → TRADITION_BY_CGROUP) carry an explicit tradition that wins anywhere;
# anything unregistered falls back to its source's home tradition below.
#
# Local-origin scrapers → the show is a HOME-GROWN work (it wasn't a registered
# import, or it'd have an explicit tradition). source substring → origin tag.
TAG_LOCAL_SRC = [
    (("opentix", "kham", "udn", "mna", "ntch"), "台灣原創"),
    (("shiki", "kageki", "toho", "j25", "theatre-orb", "japan"), "日本原創"),
    (("interpark",), "韓國原創"),
    (("jegy", "prazske", "ndm"), "歐陸原創"),
]


def classify_tag(group, source, country):
    """Origin-tradition tag. A registered work's tradition wins everywhere; an
    unregistered show inherits its local source's home tradition, else the global
    Anglo touring canon."""
    trad = TRADITION_BY_CGROUP.get(group)
    if trad:
        return trad
    src = (source or "").lower()
    for keys, tag in TAG_LOCAL_SRC:
        if any(k in src for k in keys):
            return tag
    # German/Austrian production house with an unregistered title → German-tradition.
    if "stage-entertainment" in src or country in ("Germany", "Austria", "Switzerland"):
        return "德奧音樂劇"
    return "Broadway/West End"   # the global touring canon (default for Anglo sources)


def discover_unmapped(shows):
    """Flag shows tagged as a local ORIGINAL whose title closely matches a
    REGISTERED canonical — i.e. a likely import we haven't mapped yet (we should
    add it as an alias in works.json). Writes data/_works_discover.json for review.
    Run: python scrapers/build_shows.py --discover"""
    import difflib
    canon = [(w["cgroup"], w["canonical"], w["tradition"])
             for w in {id(v): v for v in WORK_IDX.values()}.values()]
    flagged, by_tag = [], {}
    for s in shows:
        tag = s.get("tag", "")
        if "原創" not in tag:
            continue
        by_tag.setdefault(tag, []).append(s["title"])
        g = s["group"]
        best = max(canon, key=lambda c: difflib.SequenceMatcher(None, g, c[0]).ratio(),
                   default=None)
        if best:
            r = difflib.SequenceMatcher(None, g, best[0]).ratio()
            if r >= 0.82 or best[0] in g or g in best[0]:
                flagged.append({"title": s["title"], "group": g, "tagged": tag,
                                "looks_like": best[1], "would_be": best[2],
                                "ratio": round(r, 2), "city": s.get("city")})
    flagged.sort(key=lambda f: -f["ratio"])
    out = {"_comment": "Local-originals that resemble a registered work → likely "
           "unmapped imports; add the local title as an alias in works.json if so.",
           "flagged_suspected_imports": flagged,
           "all_local_originals": {k: sorted(v) for k, v in sorted(by_tag.items())}}
    (DATA / "_works_discover.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n  [discover] {len(flagged)} suspected unmapped import(s) "
          f"-> data/_works_discover.json")
    for f in flagged[:15]:
        print(f"    {f['ratio']:.2f}  {f['title'][:34]:34} ~ {f['looks_like']} ({f['would_be']})")


# Ticketmaster files AU venues by suburb — normalise to the metro people know.
AU_METRO = {
    "pyrmont": "Sydney", "haymarket": "Sydney", "leichhardt": "Sydney",
    "millers point": "Sydney", "moore park": "Sydney", "walsh bay": "Sydney",
    "burswood": "Perth", "northbridge": "Perth", "crawley": "Perth",
    "torrensville": "Adelaide", "thebarton": "Adelaide", "adelaide": "Adelaide",
    "south brisbane": "Brisbane", "brisbane": "Brisbane", "sydney": "Sydney",
    "melbourne": "Melbourne", "southbank": "Melbourne", "east perth": "Perth",
}


def main():
    by_id = {}
    sources = []
    for name in SOURCE_FILES:
        path = DATA / name
        if not path.exists():
            print(f"  skip (missing): {name}")
            continue
        blob = json.loads(path.read_text(encoding="utf-8"))
        rows = blob.get("shows", [])
        for s in rows:
            orig = clean_title(s.get("title"))
            # group from the ORIGINAL title — bilingual() may prepend the English
            # canonical ("Cats Macskák"), which group_key can no longer reduce, so
            # we fix the canonical group here and read s["group"] downstream.
            s["group"] = group_key(orig)
            s["title"] = bilingual(orig)
        for s in rows:
            by_id[s["id"]] = s
        sources.append({"file": name, "count": len(rows), "meta": blob.get("meta", {})})
        print(f"  {name}: {len(rows)} shows")

    # Ticketmaster merge — dedup purely by (show, city), NEVER by country.
    # (Country-level "covered" was a bug: one manual AU record made the whole of
    # Australia count as covered and wiped every TM AU stop, e.g. Sydney.)
    # A TM stop whose (group, city) already exists → its link is attached to the
    # existing record; otherwise it's added as a new marker.
    tm_enrich = {}
    seen_show_city = {(s["group"], city_key(s.get("city")))
                      for s in by_id.values()}
    for tm_file in (TM_FILE, "tm_tours.json"):
        tm_path = DATA / tm_file
        if not tm_path.exists():
            continue
        tm = json.loads(tm_path.read_text(encoding="utf-8")).get("shows", [])
        kept = 0
        for s in tm:
            s["title"] = clean_title(s.get("title"))
            s["group"] = gk = group_key(s["title"])
            city = city_key(s.get("city"))
            if (gk, city) in seen_show_city:
                u = s.get("attraction_url") or s.get("ticket_url")
                if u:
                    tm_enrich.setdefault((gk, city), u)
                continue
            by_id[s["id"]] = s
            seen_show_city.add((gk, city))  # also dedup TM-vs-TM across the two files
            kept += 1
        print(f"  {tm_file}: +{kept}")
        sources.append({"file": tm_file, "count": kept})

    # Drop non-musical events that slip in (mostly Ticketmaster filing film/concert/
    # comedy tours under "Musical"), e.g. "Hedwig 25th Anniversary Movie Tour" —
    # title-matched so the real "Hedwig and the Angry Inch" stays.
    nm = [i for i, s in by_id.items() if NOT_MUSICAL_RE.search(s.get("title", ""))]
    for i in nm:
        del by_id[i]
    if nm:
        print(f"  dropped {len(nm)} non-musical event(s) (movie tour / screening / concert / comedy)")

    # Ticketmaster files Australian venues under the SUBURB, not the metro
    # ("Pyrmont"/"Haymarket" → Sydney, "Burswood" → Perth) — normalise so the card
    # shows the city people know and same-city dedup works.
    for s in by_id.values():
        if s.get("country") in ("Australia", "AU"):
            metro = AU_METRO.get(city_key(s.get("city")))
            if metro:
                s["city"] = metro

    # shiki.jp is authoritative for Japan — drop other sources' Japan records of
    # shows shiki also lists (broadway.org's Japan venues proved stale, e.g.
    # Lion King listed at HARU instead of 有明四季劇場).
    shiki_groups = {s["group"] for s in by_id.values() if s.get("source") == "shiki.jp"}
    if shiki_groups:
        drop = [i for i, s in by_id.items()
                if s.get("country") == "Japan" and s.get("source") != "shiki.jp"
                and s["group"] in shiki_groups]
        for i in drop:
            del by_id[i]
        if drop:
            print(f"  dropped {len(drop)} stale Japan record(s) superseded by shiki.jp")

    # Venue-level coordinate corrections (one fix → every show at that venue).
    # Sources (Ticketmaster, geocoders) sometimes pin a venue to a same-named
    # landmark or null-island (0,0); data/venue_coords.json holds verified coords
    # keyed by "venue|city". Found via scrapers/audit_geo*.py.
    vc_path = DATA / "venue_coords.json"
    if vc_path.exists():
        vcoords = {k: v for k, v in json.loads(vc_path.read_text(encoding="utf-8")).items()
                   if not k.startswith("_")}
        fixed = 0
        for s in by_id.values():
            v = vcoords.get(venue_key(s.get("venue"), s.get("city")))
            if v and isinstance(v, list) and len(v) == 2:
                s["lat"], s["lng"] = v[0], v[1]
                fixed += 1
        print(f"  fixed {fixed} show coord(s) from venue_coords.json ({len(vcoords)} venue fixes)")

    # Booking horizon: open-ended long-runners have end_date = null; fill it with
    # their last on-sale performance from Ticketmaster (scrapers/booking_horizon.py)
    # so the timeline stops showing them indefinitely into the future.
    bh_path = DATA / "booking_horizon.json"
    if bh_path.exists():
        bh = {k: v for k, v in json.loads(bh_path.read_text(encoding="utf-8")).items()
              if not k.startswith("_")}
        n_bh = 0
        for s in by_id.values():
            d = bh.get(s["id"])
            if not d:
                continue
            if not s.get("end_date"):
                s["end_date"] = d
                s["end_rolling"] = True   # this end is the booking horizon, not a closing
                n_bh += 1
            elif s.get("onsale_only"):
                # TM city sweep truncates a busy city's later dates — replace with
                # the real last on-sale performance (sort=date,desc).
                if d != s["end_date"]:
                    s["end_date"] = d
                    n_bh += 1
        print(f"  set {n_bh} end_date(s) from booking_horizon.json (real last on-sale date)")

    # Apply manual coordinate/field corrections (source data errors).
    overrides_path = DATA / "overrides.json"
    applied = 0
    if overrides_path.exists():
        overrides = json.loads(overrides_path.read_text(encoding="utf-8"))
        for sid, patch in overrides.items():
            if sid.startswith("_") or sid not in by_id:
                continue
            for k, v in patch.items():
                if not k.startswith("_"):
                    by_id[sid][k] = v
            by_id[sid]["source"] += "+override"
            applied += 1
        print(f"  applied {applied} override(s)")

    # Merge duplicates: same show + same city listed by multiple ticket sources
    # → keep the most authoritative record, attach ALL purchase links to it.
    from collections import defaultdict
    dup = defaultdict(list)
    for s in by_id.values():
        dup[(s["group"], city_key(s.get("city")))].append(s)
    merged = 0
    for recs in dup.values():
        if len(recs) < 2:
            continue
        recs.sort(key=lambda s: (src_prio(s.get("source")),
                                 s.get("start_date") is None and s.get("end_date") is None))
        primary, rest = recs[0], recs[1:]
        links = primary.get("ticket_links") or []
        if primary.get("ticket_url") and not links:
            links = [{"label": src_label(primary.get("source")), "url": primary["ticket_url"],
                      "kind": src_kind(primary.get("source"))}]
        for r in rest:
            u = r.get("ticket_url")
            if u and all(l.get("url") != u for l in links):
                links.append({"label": src_label(r.get("source")), "url": u,
                              "kind": src_kind(r.get("source"))})
            for l in (r.get("ticket_links") or []):
                if all(x.get("url") != l.get("url") for x in links):
                    links.append({"label": l.get("label") or l.get("country") or src_label(r.get("source")),
                                  "url": l.get("url"), "kind": l.get("kind") or src_kind(r.get("source"))})
            del by_id[r["id"]]
            merged += 1
        if len(links) > 1:
            primary["ticket_links"] = links
    if merged:
        print(f"  merged {merged} duplicate show+city record(s); extra ticket links attached")

    # attach Ticketmaster show-page links to covered records (大型售票平台並列)
    enriched = 0
    for s in by_id.values():
        u = tm_enrich.get((s["group"], city_key(s.get("city"))))
        if not u or "ticketmaster" in (s.get("source") or ""):
            continue
        links = s.get("ticket_links") or (
            [{"label": src_label(s.get("source")), "url": s["ticket_url"],
              "kind": src_kind(s.get("source"))}] if s.get("ticket_url") else [])
        if all(l.get("url") != u for l in links):
            links.append({"label": "Ticketmaster", "url": u, "kind": "ticketing"})
            s["ticket_links"] = links
            enriched += 1
    if enriched:
        print(f"  attached Ticketmaster links to {enriched} existing record(s)")

    # Official production websites — region-appropriate (a UK card gets ONLY the
    # UK official site), inserted ABOVE ticketing links.
    off_path = DATA / "official_sites.json"
    if off_path.exists():
        OFF = {k: v for k, v in json.loads(off_path.read_text(encoding="utf-8")).items()
               if not k.startswith("_")}

        def region(country):
            c = country_norm(country)
            if c == "us" or c == "canada":
                return "us"
            if c in ("gb", "ireland"):
                return "uk"
            return {"australia": "au", "germany": "de", "japan": "jp", "france": "fr",
                    "spain": "es", "netherlands": "nl", "mexico": "mx", "austria": "at",
                    "switzerland": "ch", "china": "cn", "south korea": "kr"}.get(c, c)

        n_off = 0
        for s in by_id.values():
            sites = OFF.get(s["group"])
            if not sites:
                continue
            url = sites.get(region(s.get("country"))) or sites.get("global")
            if not url:
                continue
            links = s.get("ticket_links") or (
                [{"label": src_label(s.get("source")), "url": s["ticket_url"],
                  "kind": src_kind(s.get("source"))}] if s.get("ticket_url") else [])
            if s.get("ticket_url") == url:
                s["link_kind"] = "official"  # its only link IS the official site
                continue
            if all(l.get("url") != url for l in links):
                links.insert(0, {"label": "官方網站", "url": url, "kind": "official"})
                s["ticket_links"] = links
                n_off += 1
        if n_off:
            print(f"  attached region-appropriate official sites to {n_off} record(s)")

    shows = list(by_id.values())

    # link kind + tradition tag. s["group"] is already set (from the ORIGINAL title,
    # before bilingual() prepended an English canonical) — do NOT recompute it here.
    for s in shows:
        s["link_kind"] = src_kind(s.get("source"))
        s["tag"] = classify_tag(s["group"], s.get("source"), s.get("country"))

    if "--discover" in sys.argv:
        discover_unmapped(shows)

    # image inheritance: a record with no poster (e.g. a tour stop) borrows the
    # artwork from another record of the same show that has one.
    poster_by_group = {}
    for s in shows:
        if s.get("image") and s["group"] not in poster_by_group:
            poster_by_group[s["group"]] = s["image"]
    filled = 0
    for s in shows:
        if not s.get("image") and poster_by_group.get(s["group"]):
            s["image"] = poster_by_group[s["group"]]
            filled += 1
    if filled:
        print(f"  inherited {filled} poster(s) for tour/empty records")

    # tidy country names for display (USA / UK instead of the long source forms)
    COUNTRY_DISPLAY = {
        "united states of america": "USA", "united states": "USA", "usa": "USA",
        "great britain": "UK", "united kingdom": "UK", "uk": "UK",
    }
    for s in shows:
        c = (s.get("country") or "").strip()
        s["country"] = COUNTRY_DISPLAY.get(c.lower(), c)

    verified = sum(1 for s in shows if s.get("verified"))
    out = {
        "meta": {
            "source": "merged",
            "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
            "total": len(shows),
            "verified": verified,
            "unverified": len(shows) - verified,
            "sources": sources,
        },
        "shows": shows,
    }
    (DATA / "shows.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"\nWrote {len(shows)} shows -> data/shows.json ({verified} verified, {len(shows)-verified} unverified)")


if __name__ == "__main__":
    main()
