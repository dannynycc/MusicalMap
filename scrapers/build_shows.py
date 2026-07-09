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
    # Delete apostrophes BEFORE ascii-strip so the two forms agree: a straight '
    # would later become a word-break space ("you're"→"you re") while a curly ’ is
    # dropped by ascii-ignore ("you're"→"youre") — same word, divergent keys.
    t = re.sub(r"['’‘ʼ´`]", "", t)
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode()
    t = t.lower().strip()
    t = re.sub(r"^disneys?\s+(?:presents\s+)?", "", t)   # apostrophe already gone → "disneys"; strip BEFORE 'the' so
    t = re.sub(r"^the\s+", "", t)                       # "Disney's The Lion King" == "The Lion King"
    # any dash/colon marketing subtitle that mentions "musical", in any language
    # ("– Das Hit-Musical auf Schweizerdeutsch", ": The Broadway Musical", …)
    t = re.sub(r"\s*[:\-–—]\s*[^:]*musical.*$", "", t)
    t = re.sub(r"\s*[:\-–—]\s*(a\s+new\s+musical|the\s+musical|reimagined).*$", "", t)
    # trailing "the Xxx Yyy Musical" brand tails without a dash. The "the" is
    # REQUIRED — otherwise titles like "High School Musical" get over-stripped
    # to "high" (real bug: its group missed the official-site table entirely).
    # \W*$ allows trailing punctuation: "MAMMA MIA! The Musical!" (trailing "!")
    # must still strip to "mamma mia" (else it splits from "Mamma Mia!").
    t = re.sub(r"\s+the\s+(?:[\w'!\-]+\s+){0,4}musical\W*$", "", t)
    # foreign "… Il/De/El/Le/Das Musical" suffix (no dash), e.g. Italian
    # "Moulin Rouge! Il Musical", Dutch "… De Musical" → strip so it matches the
    # canonical ("moulin rouge"). The article is REQUIRED (so "High School Musical"
    # — no article before 'musical' — is left intact).
    t = re.sub(r"\s+(?:il|el|le|la|las|los|das|der|die|de|het|den)\s+musical\W*$", "", t)
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
# Traditional/Simplified Chinese converters (OpenCC, optional) — so a search alias
# stored in one script is matchable in the other ("劇院"=="剧院"). Build-only; if
# OpenCC is missing we degrade to the original script.
def _opencc(name):
    try:
        from opencc import OpenCC
        c = OpenCC(name)
        return lambda s: c.convert(s)
    except Exception:  # noqa: BLE001
        return lambda s: s


_ZH_T2S, _ZH_S2T = _opencc("t2s"), _opencc("s2t")


def _zh_both(text):
    """All script variants of a string: original + Traditional + Simplified."""
    return {text, _ZH_T2S(text), _ZH_S2T(text)}


def _load_works():
    path = DATA / "works.json"
    idx, trad_by_cgroup, aliases_by_cgroup = {}, {}, {}
    if not path.exists():
        return idx, trad_by_cgroup, aliases_by_cgroup
    for w in json.loads(path.read_text(encoding="utf-8")).get("works", []):
        cgroup = _norm(w["canonical"])
        entry = {"canonical": w["canonical"], "tradition": w.get("tradition"), "cgroup": cgroup}
        trad_by_cgroup[cgroup] = w.get("tradition")
        # every name a user might type (canonical + 中文/日文/… aliases) — and for
        # Chinese, BOTH Traditional & Simplified — so the map search matches whichever
        # script/wording the user types, even though only the canonical is displayed.
        variants = []
        for name in [w["canonical"], *w.get("aliases", [])]:
            variants.extend(_zh_both(name))
        aliases_by_cgroup[cgroup] = " ".join(dict.fromkeys(variants))
        for name in [w["canonical"], *w.get("aliases", [])]:
            idx[_norm(name)] = entry           # alias/canonical → canonical work
    return idx, trad_by_cgroup, aliases_by_cgroup


WORK_IDX, TRADITION_BY_CGROUP, ALIASES_BY_CGROUP = _load_works()


def group_key(title):
    """Registry-aware canonical group: normalise, then collapse any known alias to
    its canonical group (so 'Macskák' / 'キャッツ' / 'Cats' share one group).
    尾綴「(the/das/el/le/il) musical」摺疊:『The Addams Family Musical』與『The Addams
    Family』是同一齣,尾綴只是來源加註——去掉後再查 registry/當 group,兩種列法才會合併。"""
    t = _norm(title)
    w = WORK_IDX.get(t)
    if w:
        return w["cgroup"]
    # 只有折疊後「命中 registry」才合併——通殺會誤傷 musical 是本體/形容詞的劇名
    # (High School Musical、La Caja Musical=音樂盒、Lotería Musical…),全庫回歸驗過。
    t2 = re.sub(r"\s+(?:the|das|el|le|il|het|de)?\s*musical$", "", t).strip()
    if t2 and t2 != t:
        w2 = WORK_IDX.get(t2)
        if w2:
            return w2["cgroup"]
    return t


def resolve_work(title):
    """The registry entry a title belongs to (or None)."""
    return WORK_IDX.get(_norm(title))

# Curated sources (precise data). Order matters for de-dup: later files win.
SOURCE_FILES = ["broadway.json", "westend.json", "tours.json", "intl.json",
                "shiki.json", "takarazuka.json", "interpark.json",
                "atg.json", "stage_de.json", "madrid.json", "barcelona.json",
                "atrapalo.json", "opentix.json",
                "utiki.json", "japan.json", "easteurope.json",
                "italy.json", "sweden.json", "netherlands.json", "poland.json",
                "norway.json", "austria.json", "middleeast.json", "china.json",
                "china_poly.json", "china_ypiao.json", "china_chinaticket.json",
                "china_juooo.json", "china_damai.json",
                "portugal.json", "manual.json"]

# When several ticket sources list the SAME show in the SAME city, we keep one
# record (highest priority = most authoritative venue data) and attach every
# source's purchase link to the card. Lower index = higher priority.
# NB: atrapalo ranks ABOVE teatromadrid/teatrebarcelona — for a show both list, we
# want atrapalo to win the primary record (it's the channel we monetise via Sovrn;
# teatromadrid sells through its own 4tickets/OneBox, which earns us nothing). The
# non-monetised source's buy link still rides along (merged), so coverage is kept.
SOURCE_PRIORITY = ["shiki.jp", "kageki", "broadway-show-tickets", "londontheatre",
                   "interpark", "stage-entertainment", "atrapalo", "teatromadrid", "manual",
                   "broadway.org", "atgtickets", "ticketmaster"]
SOURCE_LABEL = {
    "broadway-show-tickets": "Broadway票務", "londontheatre": "LondonTheatre",
    "broadway.org": "Broadway.org", "shiki.jp": "四季官網", "kageki": "宝塚官網",
    "interpark": "Interpark", "atgtickets": "ATG", "stage-entertainment": "Stage官網",
    "ticketmaster": "Ticketmaster", "manual": "官方售票", "shgtheatre": "上海大劇院",
    "teatromadrid": "TeatroMadrid", "atrapalo": "Atrápalo",
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

# 同類須知但接在破折號/冒號後(TM 常見):"Beauty And The Beast - Recommended ages 6
# and Up. All guests require ticket, regardless of age" → 砍尾。關鍵字鎖定
# 年齡建議/購票規定字眼,避免誤砍真副標(如 "Sweeney Todd - The Demon Barber")。
DASH_NOTICE_RE = re.compile(
    r"\s*[-–—:]\s*[^-–—:]*(?:recommended ages?|regardless of age|require[s]? (?:a )?ticket|"
    r"all guests|babes in arms|no children under|ages? \d+ (?:and|&) (?:up|over)|premium seats?|vip seats?|18\+|21\+)[^-–—]*$", re.I)


# Trailing location/tour qualifier some sources append to disambiguate, e.g.
# Ticketmaster "Wicked (NY)" — it breaks grouping (→ a duplicate marker next to the
# already-listed New York run). Strip ONLY short location/tour qualifiers, never a
# real parenthetical like "Two Strangers (Carry a Cake Across New York)".
LOC_QUALIFIER_RE = re.compile(
    r"\s*\(\s*(?:[A-Za-z]{2}|N\.?Y\.?C?|NYC|U\.?K\.?|U\.?S\.?A?|"
    r"broadway|west\s*end|national(?:\s*tour)?|north\s*american(?:\s*tour)?|"
    r"u\.?s\.?\s*tour|uk\s*tour|on\s*tour|touring|"
    r"[A-Za-z][\w .'’&-]*,\s*[A-Za-z]{2})\s*\)\s*$", re.I)  # "(New York, NY)" / "(Cleveland, OH)"

# Performance-TYPE suffix after a dash (accessibility / special perfs) — not a
# different show. "Paddington The Musical - Relaxed Performance" → "Paddington…".
PERF_TYPE_RE = re.compile(
    r"\s*[-–—:]\s*(?:relaxed|captioned|audio[- ]?describ\w*|signed|bsl|nzsl|asl|ad\s*&\s*touch tour|(?:sign|nzsl|bsl|asl)[- ]?interpreted|"
    r"matinee|opening night|press night|gala night|previews?|sensory|autism[- ]?friendly|"
    r"dementia[- ]?friendly|touch tour|sing[- ]?along|auslan)\b.*$", re.I)


def clean_title(t):
    t = (t or "").strip()
    t = re.sub(r"\s*\|.*$", "", t)          # drop promoter pipe-tails (… | Official … Packages)
    # promoter/venue prefix → "{Show}". Handles "{Company} presents [: ] {Show}"
    # ("Lyric Theatre of Oklahoma presents Annie", "Ford's Theatre presents: Come
    # From Away") and "{Company} production of {Show}" ("NYT production of …").
    t = re.sub(r"^.{0,70}?\b(?:presents|presenta|pr[eé]sente|präsentiert|production of)\b\s*[:;]?\s+", "", t, flags=re.I)
    # 已知「主辦品牌: 劇名」前綴(冒號前綴不能通殺——SIX: The Musical 是真劇名,逐一列舉)
    t = re.sub(r"^(?:Magatzem d['’]Ars)\s*:\s*", "", t, flags=re.I)
    # 「{Show} Presented By {社區劇團}」尾綴(TM 常見)→ 取劇名本體
    t = re.sub(r"\s+Presented By\s+.{2,60}$", "", t, flags=re.I)
    # 「{作品名}, The {人物} Musical」逗號功能性副標(bio-jukebox 慣例):
    # "A Beautiful Noise, The Neil Diamond Musical" → "A Beautiful Noise"。
    # 要求 The 與 Musical 之間 ≥2 個詞(人名)——「Diana, The Musical」這種真標題不動。
    t = re.sub(r",\s*The\s+(?:[\w.'’-]+\s+){2,4}Musical\s*$", "", t)
    # 引號包劇名+行銷尾巴 → 取引號內:"'I GRIEVE DIFFERENT' written by and starring Harper Jones"
    # → "I Grieve Different"。只在「開頭就是引號劇名 + written/created/... by」時觸發,避免誤傷真副標。
    m = re.match(r"^['‘“\"](.+?)['’”\"]\s+(?:written|created|conceived|directed)\s+by\b.*$", t, flags=re.I)
    if m:
        t = m.group(1).strip()
        if t.isupper():  # TM 常全大寫;逐字 capitalize(不用 .title(),它會把 I'll 弄成 I'Ll)
            t = " ".join(w.capitalize() for w in t.split())
    prev = None
    while prev != t:
        prev = t
        t = NOTICE_RE.sub(" ", t).strip()
        t = DASH_NOTICE_RE.sub("", t).strip()
        t = LOC_QUALIFIER_RE.sub("", t).strip()
        t = PERF_TYPE_RE.sub("", t).strip()                     # "- Relaxed Performance" etc.
        t = re.sub(r"\s*\((?:19|20)\d{2}\)\s*$", "", t).strip()  # trailing year, e.g. "(1993)"
        t = re.sub(r"\s+(?:19|20)\d{2}[\s!.]*$", "", t).strip()   # trailing bare year, e.g. "… 2027"
    return re.sub(r"\s{2,}", " ", t).strip()


def strip_city_qualifier(title, city):
    """Ticketmaster appends the production's OWN city as a bare parenthetical
    ('Water for Elephants (Chicago)', 'SUFFS (Chicago)') — strip it so it groups
    with the main show. (Marker stays distinct via (group, city) dedup.) Only
    strips when the parenthetical equals this record's city, so real titles like
    'Two Strangers (Carry a Cake Across New York)' are untouched."""
    c = (city or "").split(",")[0].strip()
    if c and title:
        title = re.sub(rf"\s*\(\s*{re.escape(c)}\s*\)\s*$", "", title, flags=re.I).strip()
        # "… in Dubai" / ", en Barcelona" / ", a València" 等各語尾綴(西/加泰/法/義)
        title = re.sub(rf",?\s+(?:in|en|a|à|em|w)\s+{re.escape(c)}\s*$", "", title, flags=re.I).strip()
        # 裸接/破折號接城市尾("…80 y 90 La Puebla de Montalbán"、"…-Villanueva de la Serena"):
        # 僅當尾巴=本列城市;砍完剩太短則不砍;城市前一個字是介係詞則不砍——
        # 「Un paseo por Madrid」「Festival de Mérida」的城市是劇名本體(全庫回歸抓過的誤傷)
        m = re.search(rf"(\S+)\s+{re.escape(c)}\s*$", title, flags=re.I)
        _PREPS = {"por","de","del","della","di","da","in","von","im","zum","zur","fur","für",
                  "sur","à","au","aux","a","al","en","w","em","the","of","dans","nach"}
        if not (m and m.group(1).lower().strip("-–—,") in _PREPS and m.group(1) not in ("-","–","—",",")):
            t2 = re.sub(rf"\s*[-–—,]?\s+{re.escape(c)}\s*$", "", title, flags=re.I).strip()
            if len(t2) >= 6 and t2 != title:
                title = t2
    return title


def strip_venue_prefix(title, venue):
    """Strip a leading "{Venue}'s " that merely names the presenting house, e.g.
    "Walnut Street Theatre's THE ADDAMS FAMILY" (venue "Walnut Street Theatre")
    → "THE ADDAMS FAMILY". Only when the prefix equals THIS record's venue."""
    v = (venue or "").strip()
    if v and title:
        for pv in (v, v[4:] if v.lower().startswith("the ") else v):
            m = __import__("re").match(rf"^(?:the\s+)?{__import__('re').escape(pv)}[’']s\s+", title, flags=2)
            if m and len(title) - m.end() >= 3:
                return title[m.end():].strip()
    return title


def strip_venue_qualifier(title, venue):
    """Strip a trailing ' - {The }X' that merely names the venue, e.g. 'Jesus Christ
    Superstar - The Palladium' (venue 'London Palladium') → 'Jesus Christ Superstar'.
    Only strips when the tail is a substring of this record's venue, so real
    subtitles ('… - The Demon Barber') are left alone."""
    v = (venue or "").lower().strip()
    m = re.search(r"\s[-–—]\s*(?:the\s+)?([^-–—]+)$", title or "", flags=re.I)
    if m and v:
        tail = m.group(1).strip().lower()
        if len(tail) >= 4 and tail in v:
            return title[:m.start()].strip()
    return title


def canonical_title(title):
    """Display the work's CANONICAL name for registered works — NOT the appended
    foreign/Chinese alias (user dropped the bilingual prepend; 'Jesus Christ
    Superstar 萬世巨星' → 'Jesus Christ Superstar', 'Cats Macskák' → 'Cats').
    Unregistered local-original shows keep their own title. Aliases stay in the
    catalog search blob, so 萬世巨星 / Macskák are still searchable."""
    w = resolve_work(title)
    return w["canonical"] if w else title


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
    r"scotch college|\bjr\.?\b|\bjunior\b|"        # school/amateur: MTI Junior youth editions & college productions
    r"a very musical theatre christmas|"          # Christmas cabaret revue, not a book musical
    # TM files tribute/concert/songbook/drag acts under "Musical" — they're not
    # book musicals. Verified against the data: drops only these, no real shows.
    r"\btribute\b|\bconcert\b|\bsoundtrack\b|\bgala\b|\bcelebration\b|"
    r"\bsymphony\b|\borchestra\b|\bballett?\b|芭蕾|"   # ballet/dance — not a book musical (NOT \bopera\b: Phantom of the Opera!)
    r"\bon ice\b|\bcirque\b|circus spectacular|\bflamenco\b|opera locos|"  # ice/circus/flamenco/vocal-comedy spectacle
    r"\bthe (?:songs|music|hits) of\b|\bsongs of\b|"
    r"\bdrag (?:show|along|race|brunch|queen)\b|"
    r"\bnonstop\b|koncert|\bbluey\b|night (?:at|of) the musicals?|"  # medley/gala nights; Bluey's Big Play
    # Ticketmaster upsell listings (not a show): "… Official BJCC Ticket+ Hotel Packages",
    # VIP/suite/parking packages, meet & greet.
    r"ticket\s*\+|\b(?:hotel|vip|suite|premium|parking)\s+packages?\b|"
    r"\bofficial\b[^|]*\bpackages?\b|meet (?:and|&) greet|"
    # non-English concert/tribute words (ES/IT/TR…): 'tributo a ABBA', 'Callas en
    # concierto', 'en Acústico', 'holograma', Turkish 'Gazinosu' (cabaret/concert).
    r"\btributo\b|\bconcierto\b|ac[uú]stico|\bholograma\b|\bgazinosu\b", re.I)

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
    (("damai", "maoyan", "shcstheatre", "shgtheatre", "polyt", "chinaticket", "juooo"), "中國原創"),
]


# Country → home tradition for UNREGISTERED shows. A registered work always wins
# (its tradition is correct anywhere); this only decides where an unmapped local
# show lands, so it must NOT default everything to Broadway/West End (that put
# Spanish originals like "Hola Raffaella" on Broadway). Broadway/West End is given
# only to genuinely Anglo sources/markets + registered Anglo works.
SPANISH_C = {"Spain", "Mexico", "Argentina", "Chile", "Colombia", "Peru"}
PORTUGUESE_C = {"Brazil", "Portugal"}   # Portuguese-language originals (São Paulo, Lisbon)
GERMAN_C = {"Germany", "Austria", "Switzerland"}
ANGLO_C = {"USA", "UK", "Canada", "Australia", "New Zealand", "Ireland",
           "South Africa", "Singapore", "UAE"}
CONTINENTAL_C = {"Belgium", "Netherlands", "Denmark", "Italy", "Norway", "Sweden",
                 "Finland", "Poland", "Greece", "Croatia", "Slovenia",
                 "Romania", "Estonia", "Latvia", "Lithuania", "Bulgaria",
                 "Slovakia", "Hungary", "Czech Republic", "Turkey", "Israel"}
ANGLO_SRC = ("broadway", "londontheatre", "atgtickets")  # English-language houses


def classify_tag(group, source, country, hint=None):
    """Origin-tradition tag. A registered work's tradition wins everywhere; an
    unregistered show falls to its source/country's home tradition. Broadway/West
    End is NOT the catch-all — only Anglo sources, Anglo markets, and registered
    Anglo works get it.
    hint=scraper 從原始標題外框標記判讀的 tradition(如 OPENTIX「韓國音樂劇《…》」;
    2026-07-09 加,防止未註冊的進口授權劇掉進「來源平台=分類」誤標在地原創)——
    優先序:registry > hint > 來源/國家 fallback。"""
    trad = TRADITION_BY_CGROUP.get(group)
    if trad:
        return trad
    if hint:
        return hint
    src = (source or "").lower()
    c = country or ""
    for keys, tag in TAG_LOCAL_SRC:          # TW/JP/KR + HU/CZ local scrapers
        if any(k in src for k in keys):
            return tag
    # Spanish + Portuguese (Iberian/Latin) folded into one tradition tag 西葡音樂劇.
    if "teatromadrid" in src or c in SPANISH_C or c in PORTUGUESE_C or "bol.pt" in src:
        return "西葡音樂劇"
    # German-tradition by COUNTRY (not bare "stage-entertainment" — that also matches
    # stage-entertainment.nl and wrongly tagged Dutch shows 德奧).
    if c in GERMAN_C or "stage_de" in src or "stage-entertainment.de" in src:
        return "德奧音樂劇"
    if c == "France":
        return "法式音樂劇"
    if c == "China":
        return "中國原創"
    if any(k in src for k in ANGLO_SRC) or c in ANGLO_C:
        return "Broadway/West End"
    if c in CONTINENTAL_C:
        return "歐陸原創"
    return "Broadway/West End"   # last resort (unknown source + unknown country)


def discover_unmapped(shows):
    """Flag shows tagged as a local ORIGINAL whose title closely matches a
    REGISTERED canonical — i.e. a likely import we haven't mapped yet (we should
    add it as an alias in works.json). Writes data/_works_discover.json for review.
    Run: python scrapers/build_shows.py --discover"""
    import difflib
    canon = [(w["cgroup"], w["canonical"], w["tradition"])
             for w in {id(v): v for v in WORK_IDX.values()}.values()]
    REGIONAL = {"台灣原創", "日本原創", "韓國原創", "歐陸原創", "西葡音樂劇"}
    flagged, by_tag = [], {}
    for s in shows:
        tag = s.get("tag", "")
        if tag not in REGIONAL:
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
            orig = strip_venue_qualifier(
                strip_city_qualifier(clean_title(s.get("title")), s.get("city")),
                s.get("venue"))
            s["group"] = group_key(orig)
            s["title"] = canonical_title(orig)   # registered → canonical; else as-is
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
            orig = strip_city_qualifier(clean_title(s.get("title")), s.get("city"))
            s["group"] = gk = group_key(orig)
            s["title"] = canonical_title(orig)   # registered → canonical (Frost → Frozen)
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

    # Explicit per-title exclusions (data/not_musical.json) — plays/concerts/variety
    # shows that title patterns can't catch (verified by research). Match on _norm.
    nmt_path = DATA / "not_musical.json"
    if nmt_path.exists():
        excl = {_norm(t) for t in json.loads(nmt_path.read_text(encoding="utf-8")).get("titles", [])}
        drop = [i for i, s in by_id.items()
                if _norm(s.get("title", "")) in excl or s.get("group") in excl]
        for i in drop:
            del by_id[i]
        if drop:
            print(f"  dropped {len(drop)} non-musical(s) from not_musical.json exclusion list")

    # Ticketmaster files Australian venues under the SUBURB, not the metro
    # ("Pyrmont"/"Haymarket" → Sydney, "Burswood" → Perth) — normalise so the card
    # shows the city people know and same-city dedup works.
    for s in by_id.values():
        if s.get("country") in ("Australia", "AU"):
            metro = AU_METRO.get(city_key(s.get("city")))
            if metro:
                s["city"] = metro

    # Source-data city typos / inconsistent forms → canonical (so they merge & display
    # right, and pick up the right state/translation downstream).
    CITY_FIX = {"San Deigo": "San Diego", "Ft Lauderdale": "Fort Lauderdale", "GATINEAU": "Gatineau"}
    for s in by_id.values():
        fix = CITY_FIX.get((s.get("city") or "").strip())
        if fix:
            s["city"] = fix

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

    # Cross-source dedup: the same run can be listed by two sources (e.g. a Poly
    # theatre show appears in both polyt.cn and the ypiao aggregator). Collapse
    # records that share (group, city, venue).
    # WHO WINS: the higher-priority (more authoritative) source first. This matters
    # for West End long-runners: londontheatre marks Wicked/Lion King correctly
    # (type=resident, end=None → open-ended) while ATG mislabels them (type=tour with
    # a rolling booking horizon as a fake closing date). The old "richest data wins"
    # rule let ATG win *because* it carried an end_date — so a long-runner read like a
    # show about to close. Source priority fixes it; image/end_date are tiebreakers.
    # A record's links may live in ticket_links (list) or ticket_url (single);
    # ticket_links is only materialised later (official-site step), so read both.
    def _rec_links(x):
        if x.get("ticket_links"):
            return list(x["ticket_links"])
        if x.get("ticket_url"):
            return [{"label": src_label(x.get("source")), "url": x["ticket_url"],
                     "kind": src_kind(x.get("source"))}]
        return []

    def _merge_into(keep, drop):
        """Fold drop's ticket links + date range into keep — no booking source lost
        (so e.g. atrapalo's monetised link survives on a teatromadrid-won pin)."""
        kp, dp = by_id[keep], by_id[drop]
        merged = _rec_links(kp)
        urls = {l.get("url") for l in merged}
        for l in _rec_links(dp):
            if l.get("url") not in urls:
                merged.append(l); urls.add(l.get("url"))
        if merged:
            kp["ticket_links"] = merged
        starts = [d for d in (kp.get("start_date"), dp.get("start_date")) if d]
        ends = [d for d in (kp.get("end_date"), dp.get("end_date")) if d]
        if starts:
            kp["start_date"] = min(starts)
        # An open-ended resident/sit-down run carries end_date=None ON PURPOSE ("長期上演").
        # Don't let a merge inherit another source's booking-horizon end (e.g. ATG's
        # type=tour Wicked) — that would slap a fake closing date on a long-runner.
        open_resident = kp.get("end_date") is None and kp.get("type") in ("resident", "sit-down")
        if ends and not open_resident:
            kp["end_date"] = max(ends)

    seen_gcv = {}
    dup = []
    score = lambda x: (-src_prio(x.get("source")), bool(x.get("image")), bool(x.get("end_date")))  # noqa: E731
    for i, s in by_id.items():
        k = (s.get("group"), city_key(s.get("city")), venue_key(s.get("venue"), s.get("city")))
        if None in k or not k[0]:
            continue
        prev = seen_gcv.get(k)
        if prev is None:
            seen_gcv[k] = i
            continue
        keep, drop = (i, prev) if score(s) > score(by_id[prev]) else (prev, i)
        seen_gcv[k] = keep
        _merge_into(keep, drop)   # keep the dropped source's buy link on the surviving pin
        dup.append(drop)
    for i in dup:
        del by_id[i]
    if dup:
        print(f"  dropped {len(dup)} cross-source duplicate(s) (same show+city+venue; links merged)")

    # Venue-level COUNTRY corrections. Some sources (esp. broadway.org tours) file
    # Canadian/Mexican tour stops under "USA"; data/venue_country.json holds the true
    # country per "venue|city" (found by reverse-geocoding coords in verify_geo.py).
    # One fix → every show at that venue, so the map + theatres.html group it right.
    vco_path = DATA / "venue_country.json"
    if vco_path.exists():
        vcountry = {k: v for k, v in json.loads(vco_path.read_text(encoding="utf-8")).items()
                    if not k.startswith("_")}
        nfix = 0
        for s in by_id.values():
            fix = vcountry.get(venue_key(s.get("venue"), s.get("city")))
            if fix and s.get("country") != fix:
                s["country"] = fix
                nfix += 1
        print(f"  fixed {nfix} show country label(s) from venue_country.json")

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

    # Same-place dedup. The (group, city, venue) pass above misses the same engagement
    # listed by two sources under DIFFERENT city labels for one venue — e.g. New Wimbledon
    # Theatre as "London" (londontheatre) vs "Wimbledon" (ATG) → two pins on one point.
    # Now that coords are finalised, collapse records sharing (group, rounded coords):
    # identical coords == the same physical venue, regardless of the city/venue text.
    # The richest record survives; the other's ticket links merge in and the date range
    # widens, so no booking source is lost. (_rec_links defined above.)
    seen_gc, dropc = {}, []
    for i, s in by_id.items():
        if s.get("lat") is None or s.get("lng") is None or not s.get("group"):
            continue
        k = (s["group"], round(s["lat"], 4), round(s["lng"], 4))
        prev = seen_gc.get(k)
        if prev is None:
            seen_gc[k] = i
            continue
        # Source priority first (so the monetised channel — e.g. atrapalo over
        # teatromadrid — wins the primary record), then richest data as tiebreak.
        score = lambda x: (-src_prio(x.get("source")), bool(x.get("image")),
                           bool(x.get("start_date")), len(_rec_links(x)))  # noqa: E731
        keep, drop = (i, prev) if score(s) > score(by_id[prev]) else (prev, i)
        if keep == i:
            seen_gc[k] = i
        kp, dp = by_id[keep], by_id[drop]
        merged = _rec_links(kp)
        urls = {l.get("url") for l in merged}
        for l in _rec_links(dp):
            if l.get("url") not in urls:
                merged.append(l)
                urls.add(l.get("url"))
        if merged:
            kp["ticket_links"] = merged
        starts = [d for d in (kp.get("start_date"), dp.get("start_date")) if d]
        ends = [d for d in (kp.get("end_date"), dp.get("end_date")) if d]
        if starts:
            kp["start_date"] = min(starts)
        # An open-ended resident/sit-down run carries end_date=None ON PURPOSE ("長期上演").
        # Don't let a merge inherit another source's booking-horizon end (e.g. ATG's
        # type=tour Wicked) — that would slap a fake closing date on a long-runner.
        open_resident = kp.get("end_date") is None and kp.get("type") in ("resident", "sit-down")
        if ends and not open_resident:
            kp["end_date"] = max(ends)
        dropc.append(drop)
    for i in dropc:
        del by_id[i]
    if dropc:
        print(f"  dropped {len(dropc)} same-coord duplicate(s) (one venue listed under two city labels)")

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

    # Open-ended sit-down houses → flag end_rolling so the map shows "長期上演" not a fake
    # closing. Runs AFTER overrides so corrected dates are in play. Source-specific because
    # the sources behave differently:
    #   • broadway-show-tickets (Broadway): end_date is always the rolling booking horizon
    #     → open-ended.
    #   • londontheatre / stage-entertainment (West End / German sit-downs): open-ended ONLY
    #     when there's NO announced closing AND it has already opened. A real closing date
    #     (German limited runs, a 5-day West End show) → keep it → "至 {end}". A no-end FUTURE
    #     premiere is "upcoming" (→ "{start} 起"), not a long run — daily CI re-flags it once
    #     it opens. We deliberately DON'T trust type=resident from other sources (j25musical's
    #     1–8-day 2.5D shows are mislabeled resident).
    today = datetime.now().date()
    n_open = 0
    for s in by_id.values():
        if s.get("type") not in ("resident", "sit-down"):
            continue
        src = s.get("source") or ""
        open_run = False
        if "broadway-show-tickets" in src:
            open_run = True
        elif "broadway.org/international" in src:
            # intl.py 的頁面本來就沒日期(Lion King 巴黎/墨西哥城、Moulin Rouge 科隆等開放式定目劇);
            # 不標 rolling 會變成「日期全空」的殘缺卡(2026-07-09 日期稽核抓到,3 筆全中)。
            open_run = True
        elif "shiki" in src:
            # 劇団四季「専用劇場」=開放式定目劇(有明=獅子王 1998-、電通[海]=阿拉丁、JR東日本[春/秋]=
            # 冰雪奇緣/回到未來、舞浜=小美人魚常設)——其 end_date 是售票窗口(12/31、3/31)不是真閉幕,
            # 顯示「至 12/31」=假期間限定(2026-07-09 使用者指正)。自由劇場/名古屋/大阪=輪演檔期,保留真日期。
            _OPEN_VENUES = ("有明四季劇場", "電通四季劇場", "JR東日本四季劇場", "舞浜アンフィシアター")
            st = s.get("start_date")
            try:
                _started = datetime.fromisoformat(st).date() <= today if st else False
            except ValueError:
                _started = False
            open_run = _started and any(v in (s.get("venue") or "") for v in _OPEN_VENUES)
        elif ("londontheatre" in src or "stage-entertainment" in src) and not s.get("end_date"):
            st = s.get("start_date")
            try:
                # 完全沒日期(start 也沒有)≠ 長期上演——那是「沒抓到檔期」,不能猜成 open run
                # (Bibi&Tina 聖誕限定檔曾因此被標「長期上演」)。有 start 且已開演才算。
                open_run = datetime.fromisoformat(st).date() <= today if st else False
            except ValueError:
                open_run = False
        if open_run and not s.get("end_rolling"):
            s["end_rolling"] = True
            n_open += 1
    if n_open:
        print(f"  flagged {n_open} open-ended sit-down run(s) as long-runners (NY/West End/Stage)")

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

    # TodayTix deep links (data/todaytix.json, from scrapers/todaytix.py) — higher
    # commission than TM (~1-2% vs flat ~$0.30), so inserted as the PREFERRED ticketing
    # link (front of the list). Matched by work-group + exact city. URL is clean; the
    # affiliate wrap happens at render in js/app.js (dormant until TodayTix is approved).
    tt_path = DATA / "todaytix.json"
    if tt_path.exists():
        TT = (json.loads(tt_path.read_text(encoding="utf-8")) or {}).get("map", {})
        tt_n = 0
        for s in by_id.values():
            entries = TT.get(s["group"])
            if not entries:
                continue
            sc = (s.get("city") or "").split(",")[0].strip().lower()
            url = next((e["url"] for e in entries if e["city"].lower() == sc), None)
            if not url:
                continue
            links = s.get("ticket_links") or (
                [{"label": src_label(s.get("source")), "url": s["ticket_url"],
                  "kind": src_kind(s.get("source"))}] if s.get("ticket_url") else [])
            if all(l.get("url") != url for l in links):
                links.insert(0, {"label": "TodayTix", "url": url, "kind": "ticketing"})
                s["ticket_links"] = links
                tt_n += 1
        if tt_n:
            print(f"  attached TodayTix links to {tt_n} record(s)")

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
            reg = region(s.get("country"))
            # tours get a region-specific tour site when one exists ("us_tour" →
            # tour.wickedthemusical.com); localised sit-down productions (es/de/jp…)
            # fall through to their region site even though they're typed "tour".
            url = (sites.get(reg + "_tour") if s.get("type") == "tour" else None) \
                or sites.get(reg) or sites.get("global")
            if not url:
                continue
            links = s.get("ticket_links") or (
                [{"label": src_label(s.get("source")), "url": s["ticket_url"],
                  "kind": src_kind(s.get("source"))}] if s.get("ticket_url") else [])
            if s.get("ticket_url") == url:
                # its only link IS the official site → expose it AS the official link
                # (so the popup title hyperlinks it), not a generic ticketing tile.
                s["ticket_links"] = [{"label": "官方網站", "url": url, "kind": "official"}]
                s["link_kind"] = "official"
                continue
            existing = next((l for l in links if l.get("url") == url), None)
            if existing:
                # already present but maybe mislabeled (e.g. came in as a "Broadway.org"
                # ticketing tile) — promote it to the official site and move it to front.
                existing["label"] = "官方網站"
                existing["kind"] = "official"
                links.remove(existing)
                links.insert(0, existing)
                s["ticket_links"] = links
                n_off += 1
            else:
                links.insert(0, {"label": "官方網站", "url": url, "kind": "official"})
                s["ticket_links"] = links
                n_off += 1
        if n_off:
            print(f"  attached region-appropriate official sites to {n_off} record(s)")

    # Localized production names: many sources (Ticketmaster MX, Interpark KR, Shiki JP…)
    # only give the canonical English title. data/local_titles.json maps group+region to
    # the real local production name (El Rey León, ライオンキング…) so the popup shows it.
    lt_path = DATA / "local_titles.json"
    if lt_path.exists():
        LT = {k: v for k, v in json.loads(lt_path.read_text(encoding="utf-8")).items() if not k.startswith("_")}
        def _lt_region(country):
            c = country_norm(country)
            if c in ("us", "canada"):
                return "us"
            if c in ("gb", "ireland"):
                return "uk"
            return {"australia": "au", "germany": "de", "japan": "jp", "france": "fr",
                    "spain": "es", "netherlands": "nl", "mexico": "mx", "austria": "at",
                    "switzerland": "ch", "china": "cn", "south korea": "kr"}.get(c, c)
        n_lt = 0
        for s in by_id.values():
            if s.get("tour_name"):
                continue
            name = (LT.get(s["group"]) or {}).get(_lt_region(s.get("country")))
            if name:
                s["tour_name"] = name
                n_lt += 1
        if n_lt:
            print(f"  set local production names on {n_lt} record(s)")

    # Backfill missing tour_name on US/Canada tour legs from a sibling stop of the same
    # group (same national tour, scraped from a source that didn't carry the name), so
    # every leg shows the production's real name instead of the bare show title.
    from collections import Counter
    grp_tn = {}
    for s in by_id.values():
        if s.get("type") == "tour" and country_norm(s.get("country")) in ("us", "canada") and s.get("tour_name"):
            grp_tn.setdefault(s["group"], Counter())[s["tour_name"]] += 1
    n_bf = 0
    for s in by_id.values():
        if s.get("type") == "tour" and country_norm(s.get("country")) in ("us", "canada") and not s.get("tour_name"):
            names = grp_tn.get(s["group"])
            if names:
                s["tour_name"] = names.most_common(1)[0][0]
                n_bf += 1
    if n_bf:
        print(f"  backfilled tour_name on {n_bf} record(s) from sibling tour stops")

    shows = list(by_id.values())

    # link kind + tradition tag + search aliases. s["group"] is already set (from the
    # original title) — do NOT recompute it here.
    for s in shows:
        s["link_kind"] = src_kind(s.get("source"))
        s["tag"] = classify_tag(s["group"], s.get("source"), s.get("country"), s.get("tag_hint"))
        # TM 常全大寫列名("THE ADDAMS FAMILY"):命中 registry 就用 canonical 正名;
        # 沒命中的(匈/捷原文慣例大寫)不動
        _t = s.get("title") or ""
        if len(_t) > 7 and _t.upper() == _t and re.search(r"[A-Z]{4}", _t):
            _w = resolve_work(_t)
            if _w:
                s["title"] = _w["canonical"]
        alt = ALIASES_BY_CGROUP.get(s["group"])   # 中文/日文… aliases, for map search
        if alt and alt.lower() != (s.get("title") or "").lower():
            s["alt"] = alt

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

    # 大麥精準連結升級:中國各來源(保利/聚橙/ypiao/上海文廣…)的售票連結常是大麥「搜尋頁」
    # (search.damai.cn,點進去一堆場次)。大麥手動批次(china_damai.json)已抓到精準 detail 連結
    # (直達該場)→ 用 (group, 城市) 查找表,把任何來源的搜尋頁連結換成精準連結。
    # 此步每次 CI build 都跑,故隔天新抓的保利/聚橙資料也會自動升級(大麥本身手動更新)。
    damai_idx = {}
    dd_path = DATA / "china_damai.json"
    if dd_path.exists():
        try:
            for ds in json.loads(dd_path.read_text(encoding="utf-8")).get("shows", []):
                u = ds.get("ticket_url") or ""
                if "detail.damai.cn" not in u:
                    continue
                g = group_key(ds.get("title", ""))
                for c in (ds.get("city"), ds.get("city_cn")):   # 英/中城市名都建 key
                    if c:
                        damai_idx[(g, c.strip().lower())] = u
        except Exception as e:  # noqa: BLE001
            print(f"  [damai-idx] skipped: {e}")

    upgraded = 0
    for s in shows:
        links = s.get("ticket_links") or []
        precise = damai_idx.get((s.get("group"), (s.get("city") or "").strip().lower()))
        # 1) 把該場任何 search.damai.cn 連結換成精準 detail(查找表命中時)
        if precise:
            for l in links:
                if "search.damai.cn" in (l.get("url") or ""):
                    l["url"] = precise
                    upgraded += 1
            if "search.damai.cn" in (s.get("ticket_url") or ""):
                s["ticket_url"] = precise
        # 2) 同場若有 detail 連結,移除殘留的搜尋頁連結(避免並列重複)
        if any("detail.damai.cn" in (l.get("url") or "") for l in links):
            kept = [l for l in links if "search.damai.cn" not in (l.get("url") or "")]
            if len(kept) != len(links):
                s["ticket_links"] = kept
            if "search.damai.cn" in (s.get("ticket_url") or ""):
                s["ticket_url"] = next(l["url"] for l in (s.get("ticket_links") or [])
                                       if "detail.damai.cn" in (l.get("url") or ""))
    if upgraded:
        print(f"  upgraded {upgraded} damai search-link(s) → precise detail link (via china_damai lookup)")

    # 中國售票連結 label 按目的地 host 統一(不同來源各自命名,如保利把大麥連結標「售票連結」、
    # 大麥 scraper 標「大麥」→ 同一齣劇不同城市標籤不一致)。依 host 正規化成品牌名,讓使用者一眼
    # 認得去哪買;ticket_url-only 的也補成 ticket_links 免得 fallback 顯示泛用字。
    CN_HOST_LABEL = [("damai.cn", "大麥"), ("juooo.com", "聚橙"), ("maoyan.com", "貓眼"),
                     ("polyt.cn", "保利票務"), ("ypiao", "票務")]
    relabeled = 0
    for s in shows:
        links = s.get("ticket_links")
        if not links and s.get("ticket_url"):      # 只有 ticket_url → 補 ticket_links
            links = [{"url": s["ticket_url"], "kind": s.get("link_kind") or "ticketing"}]
            s["ticket_links"] = links
        for l in (links or []):
            if l.get("kind") == "official":
                continue
            host = (l.get("url") or "").lower()
            for key, name in CN_HOST_LABEL:
                if key in host and l.get("label") != name:
                    l["label"] = name
                    relabeled += 1
                    break
    if relabeled:
        print(f"  relabeled {relabeled} China ticket link(s) by destination host")

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
