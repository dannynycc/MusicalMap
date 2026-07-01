"""Generate data/venues_catalog.json — autocomplete dictionary for the personal
"log a musical" form (venues, cities, bilingual titles, currencies, posters).

Run: python scrapers/gen_catalog.py
"""

import html as htmllib
import json
import math
import re
import unicodedata
from pathlib import Path

# group_key + utf-8 stdout come from build_shows (importing it sets stdout; don't
# re-wrap here or the orphaned wrapper GC-closes the buffer).
from build_shows import group_key

DATA = Path(__file__).resolve().parent.parent / "data"

# Registered works → canonical English title, so a group's catalog `en` is the clean
# canonical (matching what users log) instead of an arbitrary first/bilingual title
# (e.g. "Gutenberg! The Musical! Gutenberg, el mejor…" → "Gutenberg! The Musical!").
def _load_works():
    """Return (canon, by_group): canon = group_key -> canonical English title;
    by_group = group_key -> full work dict (poster, productions, aliases…).
    works.json is now the作品主檔 — it also carries non-playing works (e.g. Love
    Never Dies) and per-work production posters, all keyed by the canonical's group."""
    p = DATA / "works.json"
    if not p.exists():
        return {}, {}
    ws = json.loads(p.read_text(encoding="utf-8")).get("works", [])
    canon, by_group = {}, {}
    for w in ws:
        g = group_key(w["canonical"])
        canon[g] = w["canonical"]
        by_group[g] = w
    return canon, by_group


CANON, WORKS = _load_works()

# Traditional/Simplified Chinese folding so a venue/title is found whichever script
# the user types (上海大劇院 = 上海大剧院, 台北 = 臺北 …). OpenCC is build-only; if
# unavailable we degrade to no conversion (still searchable in the original script).
def _opencc(name):
    """Return an OpenCC convert fn for `name`, or identity if unavailable —
    each converter independent so one missing config can't disable the others."""
    try:
        from opencc import OpenCC
        c = OpenCC(name)
        return lambda s: c.convert(s)
    except Exception:  # noqa: BLE001 — opencc optional
        return lambda s: s


_t2s = _opencc("t2s")   # Traditional → Simplified
_s2t = _opencc("s2t")   # Simplified → Traditional

# opencc-python-reimplemented ships no jp2t config, so map the Japanese shinjitai
# that differ from BOTH Chinese forms (notably 芸→藝) to Traditional, so a Chinese
# user typing 藝術 finds the Japanese-named 梅田芸術劇場.
_JP2T_MAP = str.maketrans({
    "芸": "藝", "国": "國", "会": "會", "県": "縣", "楽": "樂", "観": "觀", "庁": "廳",
    "営": "營", "体": "體", "学": "學", "数": "數", "円": "圓", "売": "賣", "図": "圖",
    "戦": "戰", "浜": "濱", "沢": "澤", "駅": "驛", "区": "區", "随": "隨", "続": "續",
    "歓": "歡", "騒": "騷", "両": "兩", "齢": "齡", "豊": "豐", "戯": "戲",
})
def _jp2t(s): return (s or "").translate(_JP2T_MAP)

# common Taiwanese variant character not always covered by t2s/s2t mappings
_VARIANT = str.maketrans({"臺": "台"})

# brackets/quotes in EVERY width & style — half-width, full-width, CJK, curly —
# folded to spaces so "電通四季劇場[海]" and "電通四季劇場" match either way, and
# typing with or without （）［］「」＂＇""'' makes no difference.
_PUNCT = re.compile(r"""[()\[\]{}（）［］｛｝「」『』【】〔〕《》〈〉<>＜＞"'`＂＇“”‘’｀、・·,，:：/／|｜~～\-－—–]+""")


# strip Latin diacritics so "madach" finds "Madách", "munchen"→"München", "lodz"→"Łódź".
# Only Latin letters are folded — CJK/kana/Hangul/Cyrillic/Greek are left intact
# (folding kana would wrongly merge ガ→カ).
_FOLD_EXTRA = {"ł": "l", "Ł": "l", "ø": "o", "Ø": "o", "ß": "ss", "đ": "d", "Đ": "d",
               "æ": "ae", "Æ": "ae", "œ": "oe", "Œ": "oe", "ı": "i", "ð": "d", "þ": "th"}


def _fold(s):
    out = []
    for ch in (s or ""):
        if ch in _FOLD_EXTRA:
            out.append(_FOLD_EXTRA[ch]); continue
        d = unicodedata.normalize("NFKD", ch)
        if d and ord(d[0]) < 128 and d[0].isalpha():        # Latin base → drop accents
            out.append("".join(x for x in d if not unicodedata.combining(x)))
        else:
            out.append(ch)                                   # keep non-Latin scripts
    return "".join(out)


def _clean(s):
    return re.sub(r"\s+", " ", _PUNCT.sub(" ", _fold(s or ""))).strip()


def _distm(a, b, c, d):
    R = 6371008.8; p = math.pi / 180
    h = 0.5 - math.cos((c-a)*p)/2 + math.cos(a*p)*math.cos(c*p)*(1-math.cos((d-b)*p))/2
    return 2 * R * math.asin(math.sqrt(h))


_CJK = re.compile("[぀-ヿ㐀-鿿가-힯＀-￯]")


def _has_latin_only(s):
    """True if the name has no CJK/Hangul/Kana (i.e. already a Latin-script name)."""
    return not _CJK.search(s or "")


def search_blob(*parts):
    """Lowercased searchable string: every part plus its simplified/traditional and
    臺→台 folded forms, so any script/variant the user types matches."""
    seen = []
    for p in parts:
        jt = _jp2t(p or "")                # Japanese shinjitai → Traditional (芸術→藝術)
        forms = {p, _t2s(p), _s2t(p), (p or "").translate(_VARIANT), jt, _t2s(jt)}
        for form in forms:
            f = _clean(form).lower()       # fold away all brackets/quotes/punct
            if f and f not in seen:
                seen.append(f)
    return " ".join(seen)

# Curated venues missing from the musical dataset (name, city, country, lat, lng).
# Taiwan / Japan / Korea now come from the richer data/{tw,jp,kr}_venues.json
# (bilingual + Google coords); only the few remaining gaps are kept here.
CURATED = [
    ("Hong Kong Cultural Centre", "Hong Kong", "Hong Kong", 22.2940, 114.1700),
    ("Esplanade Theatre (濱海藝術中心)", "Singapore", "Singapore", 1.2897, 103.8559),
    ("Sands Theatre, Marina Bay Sands (濱海灣金沙劇院)", "Singapore", "Singapore", 1.2847, 103.8590),
    ("Sydney Opera House", "Sydney", "Australia", -33.8568, 151.2153),
    ("Théâtre du Châtelet", "Paris", "France", 48.8576, 2.3470),
    ("Teatro alla Scala", "Milan", "Italy", 45.4674, 9.1895),
    ("Raimund Theater", "Vienna", "Austria", 48.1969, 16.3438),
    ("Ronacher", "Vienna", "Austria", 48.2073, 16.3760),
    # Philippines (Google-geocoded) — big international-tour houses in Metro Manila + Cebu/Davao
    ("The Theatre at Solaire", "Pasay", "Philippines", 14.522812, 120.983461),
    ("CCP Main Theater (Tanghalang Nicanor Abelardo)", "Pasay", "Philippines", 14.558412, 120.985911),
    ("Newport Performing Arts Theater", "Pasay", "Philippines", 14.519111, 121.020059),
    ("Meralco Theater", "Pasig", "Philippines", 14.589851, 121.063900),
    ("SM Mall of Asia Arena", "Pasay", "Philippines", 14.531636, 120.984023),
    ("Smart Araneta Coliseum", "Quezon City", "Philippines", 14.620667, 121.053397),
    ("Cebu Cultural Center", "Cebu", "Philippines", 10.322537, 123.899211),
    ("SMX Convention Center Davao", "Davao", "Philippines", 7.098812, 125.630241),
    # Singapore (Esplanade + Sands already above) — remaining big-musical houses
    ("The Star Theatre (星宇表演藝術中心)", "Singapore", "Singapore", 1.306842, 103.788440),
    ("Resorts World Theatre (聖淘沙名勝世界劇場)", "Singapore", "Singapore", 1.255179, 103.821811),
    ("Singapore Indoor Stadium (新加坡室內體育館)", "Singapore", "Singapore", 1.300571, 103.874394),
    ("Victoria Theatre (維多利亞劇院)", "Singapore", "Singapore", 1.288621, 103.851462),
    ("Drama Centre Theatre (戲劇中心劇院)", "Singapore", "Singapore", 1.297571, 103.854291),
    # Thailand — big international-tour + flagship local houses (mostly Bangkok)
    ("Muangthai Rachadalai Theatre (泰國創意劇場)", "Bangkok", "Thailand", 13.766803, 100.569473),
    ("Thailand Cultural Centre Main Hall (泰國文化中心)", "Bangkok", "Thailand", 13.766677, 100.574196),
    ("Prince Mahidol Hall (瑪希敦王子展演廳)", "Nakhon Pathom", "Thailand", 13.789575, 100.321160),
    ("Aksra Theatre King Power (阿克薩拉劇院)", "Bangkok", "Thailand", 13.759503, 100.537886),
    ("Ultra Arena Bravo BKK", "Bangkok", "Thailand", 13.750749, 100.572318),
    ("KBank Siam Pic-Ganesha Theatre (暹羅百麗宮迦納薩劇院)", "Bangkok", "Thailand", 13.744902, 100.533775),
    ("IMPACT Arena", "Nonthaburi", "Thailand", 13.912606, 100.547753),
    ("Siam Niramit Phuket (暹羅夢幻劇場)", "Phuket", "Thailand", 7.932230, 98.375703),
    # Malaysia — Kuala Lumpur / Selangor + Genting / Malacca / Penang
    ("Istana Budaya (國家文化宮)", "Kuala Lumpur", "Malaysia", 3.174352, 101.703824),
    ("Dewan Filharmonik Petronas (國油管弦樂廳)", "Kuala Lumpur", "Malaysia", 3.158212, 101.711526),
    ("KLPAC Pentas 1", "Kuala Lumpur", "Malaysia", 3.185170, 101.686392),
    ("Panggung Bandaraya DBKL (城市劇院)", "Kuala Lumpur", "Malaysia", 3.150255, 101.694893),
    ("PJPAC Stage 1", "Petaling Jaya", "Malaysia", 3.148095, 101.617251),
    ("DPAC Theatre", "Petaling Jaya", "Malaysia", 3.166679, 101.612253),
    ("The Platform @ Menara Ken TTDI", "Kuala Lumpur", "Malaysia", 3.152374, 101.622372),
    ("CPAC Dato' Pilus Hall", "Petaling Jaya", "Malaysia", 3.151542, 101.656779),
    ("Axiata Arena (亞通體育館)", "Kuala Lumpur", "Malaysia", 3.053815, 101.693434),
    ("Arena of Stars (雲星劇場)", "Genting Highlands", "Malaysia", 3.422520, 101.793710),
    ("Encore Melaka (又見馬六甲)", "Malacca", "Malaysia", 2.187342, 102.220942),
    ("Dewan Sri Pinang (檳城大會堂)", "George Town", "Malaysia", 5.421764, 100.340649),
]

# Confident, standard Chinese names (searchable alongside English). Only well-
# established translations — uncertain ones are intentionally omitted, not guessed.
ZH = {
    "the phantom of the opera": "歌劇魅影", "phantom of the opera": "歌劇魅影",
    "les miserables": "悲慘世界", "miss saigon": "西貢小姐", "cats": "貓",
    "the lion king": "獅子王", "mamma mia": "媽媽咪呀", "chicago": "芝加哥",
    "wicked": "女巫前傳", "beauty and the beast": "美女與野獸", "aladdin": "阿拉丁",
    "frozen": "冰雪奇緣", "cinderella": "仙履奇緣", "the little mermaid": "小美人魚",
    "the sound of music": "真善美", "mary poppins": "歡樂滿人間", "matilda": "瑪蒂達",
    "hairspray": "髮膠明星夢", "moulin rouge": "紅磨坊", "elisabeth": "伊麗莎白",
    "tanz der vampire": "吸血鬼之舞", "mozart": "莫札特", "rebecca": "蝴蝶夢",
    "the hunchback of notre dame": "鐘樓怪人", "tarzan": "泰山",
    "back to the future": "回到未來", "mrs doubtfire": "窈窕奶爸",
    "pretty woman": "麻雀變鳳凰", "dirty dancing": "熱舞17", "grease": "火爆浪子",
    "jesus christ superstar": "萬世巨星", "evita": "艾薇塔", "anastasia": "真假公主",
    "tootsie": "窈窕淑男", "a chorus line": "歌舞線上", "the producers": "金牌製作人",
    "billy elliot": "舞動人生", "hercules": "大力士", "romeo et juliette": "羅密歐與茱麗葉",
    "the book of mormon": "摩門經", "sunset boulevard": "日落大道",
    "love never dies": "愛無止盡",
}

# 分組常去掉開頭冠詞（"The Lion King" → group "lion king"），但 ZH 的 key 可能帶
# "the"（如 "the lion king"）。查表時兩邊都剝掉開頭 the/a/an 再比，否則帶冠詞的
# 譯名（Lion King / Little Mermaid / Book of Mormon…）會對不上 group 而漏掉中文名。
def _zh_key(s):
    s = re.sub(r"[^a-z0-9 ]", "", (s or "").lower()).strip()
    return re.sub(r"^(the|a|an) ", "", s)
_ZH_LOOKUP = {_zh_key(k): v for k, v in ZH.items()}

# Currencies covering every country in the dataset + common ones, ISO 4217.
CURRENCIES = [
    "TWD 新台幣", "USD 美元", "GBP 英鎊", "EUR 歐元", "JPY 日圓", "KRW 韓元",
    "CNY 人民幣", "HKD 港幣", "SGD 新加坡幣", "AUD 澳幣", "NZD 紐西蘭幣",
    "CAD 加幣", "CHF 瑞士法郎", "CZK 捷克克朗", "MXN 墨西哥披索", "THB 泰銖",
    "MYR 馬來西亞令吉", "PHP 菲律賓披索", "IDR 印尼盾", "VND 越南盾", "INR 印度盧比",
    "MOP 澳門幣", "SEK 瑞典克朗", "NOK 挪威克朗", "DKK 丹麥克朗", "PLN 波蘭茲羅提",
    "HUF 匈牙利福林", "RON 羅馬尼亞列伊", "BRL 巴西雷亞爾", "ZAR 南非蘭特",
    "AED 阿聯酋迪拉姆", "ILS 以色列新謝克爾", "TRY 土耳其里拉", "RUB 俄羅斯盧布",
]


# generic words that don't distinguish one theatre from another
STOP = {"the", "a", "an", "for", "of", "at", "on", "and", "theatre", "theater",
        "arts", "art", "performing", "center", "centre", "hall", "playhouse",
        "auditorium", "stage", "perf"}


def norm_venue(name, city=""):
    """Order-independent token-set key, ignoring generic words and the city name,
    so naming variants merge ('Liverpool Empire' == 'Liverpool Empire Theatre',
    'Fox Theatre' == 'Fox Theatre - Atlanta') while genuinely different venues
    in the same city stay separate."""
    n = htmllib.unescape(name).lower()
    n = re.sub(r"\([^)]*\)", " ", n).replace("&", " and ")
    city_toks = set(re.sub(r"[^a-z0-9 ]", " ", htmllib.unescape((city or "").lower())).split())
    toks = [w for w in re.sub(r"[^a-z0-9 ]", " ", n).split()
            if len(w) > 1 and w not in STOP and w not in city_toks]
    return tuple(sorted(set(toks)))


def vkey(venue, city):
    return f"{(venue or '').strip().lower()}|{(city or '').lower().split(',')[0].strip()}"


def main():
    shows = json.loads((DATA / "shows.json").read_text(encoding="utf-8"))["shows"]
    vnames_path = DATA / "venue_names.json"   # vkey -> {en, native} for Asian venues
    vnames = json.loads(vnames_path.read_text(encoding="utf-8")) if vnames_path.exists() else {}

    # venues — dedup by (normalized name, city); keep the longest/cleanest display
    vmerge = {}
    def add_venue(name, city, country, lat, lng):
        if not name or lat is None:
            return
        name = re.sub(r"\s{2,}", " ", htmllib.unescape(name)).strip()  # fix &#039; / &amp;
        city = (city or "").strip()
        nk = norm_venue(name, city)
        if not nk:
            # all distinctive words were the city name (e.g. "San Jose Center for the
            # Performing Arts") — retry keeping city tokens so variants still dedupe.
            nk = norm_venue(name, "")
        if not nk:
            # pure CJK/Hangul name (no Latin tokens) — DON'T drop it; key on the
            # bracket-stripped name so e.g. 大阪四季劇場 / 有明四季劇場 survive.
            nk = (re.sub(r"[\s()\[\]（）［］「」『』]+", "", name.lower()),)
            if not nk[0]:
                return
        k = (nk, city.lower().split(",")[0].strip())
        cur = vmerge.get(k)
        # prefer the shorter, cleaner display name (no "- City" / section suffix)
        if not cur or len(name) < len(cur["name"]):
            vmerge[k] = {"name": name, "city": city, "country": country or (cur or {}).get("country", ""),
                         "lat": lat, "lng": lng}
        elif not cur.get("country") and country:
            cur["country"] = country
    for s in shows:
        add_venue(s.get("venue"), s.get("city"), s.get("country"), s.get("lat"), s.get("lng"))
    for name, city, country, lat, lng in CURATED:
        add_venue(name, city, country, lat, lng)

    # finalize venues: bilingual display ("English 原文") + a search blob covering
    # English + native + simplified/traditional + 臺/台, so any script/variant matches.
    venues = []
    for v in vmerge.values():
        raw, city = v["name"], v["city"]
        bi = vnames.get(vkey(raw, city)) or {}
        en, native = bi.get("en", ""), bi.get("native", "")
        if en and native and native.strip() != en.strip():
            display = f"{en} {native}"
        elif en and not _has_latin_only(raw):       # raw is non-Latin → prefer English-led display
            display = f"{en} {raw}" if raw not in en else en
        else:
            display = raw
        v["name"] = re.sub(r"\s{2,}", " ", display).strip()
        v["search"] = search_blob(raw, en, native)
        venues.append(v)

    # curated regional venue lists (Taiwan / Japan / Korea …) — bilingual halls that
    # host musicals but have no "currently playing" run, so they only enrich the
    # My-Musicals autocomplete. Display "English 原文"; search covers EN + native + 中文.
    ckey = lambda c: (c or "").lower().split(",")[0].strip()
    idx = {}  # city -> [venue dicts]; reused both to dedupe AND to enrich existing
    for v in venues:
        idx.setdefault(ckey(v["city"]), []).append(v)
    def match(city, *names):
        # probe with the FULL local name(s) only (not the English name): distinct
        # halls of one building share an English name (National Taichung Theater 大/
        # 中/小劇場) and must NOT collapse, while a true duplicate (same native name
        # from a show) still merges. Compare space-insensitively too, since a show's
        # venue ("臺中國家歌劇院中劇院") and the curated one ("臺中國家歌劇院 中劇院")
        # differ only by spacing.
        probes = [_clean(n).lower() for n in names if n and len(_clean(n)) > 3]
        for v in idx.get(ckey(city), []):
            blob = v["search"]; blob_ns = blob.replace(" ", "")
            if any(p in blob or p.replace(" ", "") in blob_ns for p in probes):
                return v
        return None
    for fname in ("tw_venues.json", "jp_venues.json", "kr_venues.json", "cn_venues.json",
                  "eu_venues.json", "row_venues.json"):
        fp = DATA / fname
        if not fp.exists():
            continue
        added = merged = 0
        for v in json.loads(fp.read_text(encoding="utf-8")):
            if not v.get("lat"):
                continue
            en, zh, native = v.get("en", ""), v.get("zh", ""), v.get("native", "")
            city, country = v.get("city", ""), v.get("country", "")
            extra = zh or native
            display = f"{en} {extra}".strip() if (en and extra) else (en or extra)
            blob = search_blob(en, native, zh)
            hit = match(city, zh, native)   # match on full local name, not shared EN
            if hit:   # already present from a show — fold in the extra names/scripts
                # concatenate blobs (keep phrases intact for multi-word matches like
                # "blue square") rather than tokenizing, which would scramble order.
                hit["search"] = (hit["search"] + " " + blob).strip()
                # prefer the curated bilingual display when the existing name lacks the
                # English part (e.g. a show venue "臺中國家歌劇院中劇院" → upgrade to
                # "National Taichung Theater 臺中國家歌劇院 中劇院").
                if en and en.lower() not in hit["name"].lower() and display:
                    hit["name"] = re.sub(r"\s{2,}", " ", display).strip()
                merged += 1
                continue
            rec = {"name": re.sub(r"\s{2,}", " ", display).strip(), "city": city, "country": country,
                   "lat": v["lat"], "lng": v["lng"], "search": blob}
            venues.append(rec)
            idx.setdefault(ckey(city), []).append(rec)
            added += 1
        print(f"  + {added} new, {merged} merged from {fname}")

    # deep-discovered EU venues (Google Places crawl) — single-point POIs with no
    # sub-hall semantics, so here we MAY dedup by coordinate proximity (<=55 m) as
    # well as by name, to drop ones already present from shows/curated.
    for disc_name in ("eu_discovered.json", "na_discovered.json", "gb_discovered.json"):
      disc = DATA / disc_name
      if disc.exists():
        dn = 0
        for v in json.loads(disc.read_text(encoding="utf-8")):
            if not v.get("lat"):
                continue
            en, native = v.get("en", ""), v.get("native", "")
            city, country = v.get("city", ""), v.get("country", "")
            nm = _clean(en or native).lower()
            dup = None
            for u in idx.get(ckey(city), []):
                if (len(nm) > 3 and nm in u["search"]) or \
                   (isinstance(u.get("lat"), (int, float)) and _distm(v["lat"], v["lng"], u["lat"], u["lng"]) <= 55):
                    dup = u; break
            blob = search_blob(en, native)
            if dup:
                dup["search"] = (dup["search"] + " " + blob).strip()
                continue
            display = f"{en} {native}".strip() if (en and native) else (en or native)
            rec = {"name": re.sub(r"\s{2,}", " ", display).strip(), "city": city,
                   "country": country, "lat": v["lat"], "lng": v["lng"], "search": blob}
            venues.append(rec); idx.setdefault(ckey(city), []).append(rec); dn += 1
        print(f"  + {dn} discovered venues from {disc_name} (deduped)")

    # explicit alias merges — the SAME venue listed under name variants (user-confirmed).
    # Distinct halls in one building (Tokyo Forum Hall A/C, 大/中/小劇場…) are NOT here.
    # (city substring, canonical display name, [name substrings that collapse into it])
    ALIAS_MERGES = [
        ("appleton", "Fox Cities Performing Arts Center", ["fox cities"]),
        ("cleveland", "KeyBank State Theatre", ["keybank state"]),
        ("little rock", "Robinson Center", ["robinson cent", "robinson perf"]),
        ("los angeles", "Hollywood Pantages Theatre", ["pantages"]),
        ("new york", "Hard Rock Cafe - NYC", ["hard rock cafe"]),
        ("orlando", "Dr. Phillips Center for the Performing Arts", ["dr. phillips", "dr phillips"]),
        ("philadelphia", "Academy of Music", ["academy of music"]),
        ("tampa", "Straz Center for the Performing Arts", ["straz cent", "carol morsani"]),
        ("worcester", "The Hanover Theatre", ["hanover theatre"]),
    ]
    alias_merged = 0
    for city_sub, canonical, subs in ALIAS_MERGES:
        hits = [v for v in venues if city_sub in ckey(v["city"])
                and any(s in v["name"].lower() for s in subs)]
        if len(hits) < 2:
            continue
        keep = hits[0]
        keep["name"] = canonical
        for v in hits[1:]:
            keep["search"] = (keep["search"] + " " + v["search"]).strip()
            venues.remove(v)
            alias_merged += 1
    print(f"  alias-merged {alias_merged} duplicate venue(s)")

    cities = sorted({(s.get("city"), s.get("country") or "") for s in shows if s.get("city")})

    # bilingual titles + poster per show-group. group_shows keeps every show of a
    # group so we can cluster them into per-country "productions" below.
    groups, posters, group_shows = {}, {}, {}
    for s in shows:
        g = s.get("group") or s["title"].lower()
        groups.setdefault(g, s["title"])
        group_shows.setdefault(g, []).append(s)
        if s.get("image") and g not in posters:
            posters[g] = s["image"]

    # work-level poster override: a registered work may pin its own canonical poster
    # (works.json `poster`), winning over an arbitrary first-scraped image. "auto"/
    # absent keeps the scraped one. Non-playing works (no show) get their pinned one.
    for g, w in WORKS.items():
        pv = w.get("poster")
        if pv and pv != "auto":
            posters[g] = pv

    # ----- productions per work-group: live auto-clusters + archival from works.json
    # live: a work playing in >=2 countries (or that ALSO has archival entries) is
    # split per country, each with a representative scraped poster. Single-country
    # works need no split — the work-level poster already represents them.
    def _city_label(grp):
        cs = sorted({(s.get("city") or "").strip() for s in grp if s.get("city")})
        return cs[0] if len(cs) == 1 else ""

    productions = {}
    for g, first_title in groups.items():
        archival = list((WORKS.get(g) or {}).get("productions") or [])
        by_country = {}
        for s in group_shows.get(g, []):
            by_country.setdefault(s.get("country") or "—", []).append(s)
        live = []
        if len(by_country) >= 2 or archival:
            for ctry, grp in sorted(by_country.items()):
                city = _city_label(grp)
                img = next((s["image"] for s in grp if s.get("image")), None)
                live.append({
                    "key": f"{g}::{ctry}",
                    "label": f"{city}, {ctry}" if city else ctry,
                    "label_zh": "", "poster": img, "origin": "live",
                })
        prods = archival + live          # archival (curated) listed first
        if len(prods) >= 2:
            productions[g] = prods

    # titles: every show-group UNION every registered work (so works that are not
    # currently playing — e.g. Love Never Dies — still appear in autocomplete).
    title_groups = dict(groups)
    for g, w in WORKS.items():
        title_groups.setdefault(g, w["canonical"])
    titles = []
    for g, first_title in sorted(title_groups.items(), key=lambda x: x[1].lower()):
        # registered work → clean canonical; else the (non-bilingual) scraped title
        en = CANON.get(g, first_title)
        zh = _ZH_LOOKUP.get(_zh_key(g))
        w = WORKS.get(g) or {}
        # keep the bilingual/variant title + every works.json alias searchable
        titles.append({"en": en, "zh": zh, "group": g,
                       "search": search_blob(en, first_title, zh or "", *w.get("aliases", []))})

    out = {
        "venues": sorted(venues, key=lambda v: v["name"]),
        "cities": [{"city": c, "country": k} for c, k in cities],
        "titles": titles,
        "currencies": CURRENCIES,
        "posters": posters,         # group_key -> work-level poster (map cards / fallback)
        "productions": productions,  # group_key -> [{key,label,poster,origin}] for the footprint version picker
    }
    (DATA / "venues_catalog.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"venues {len(out['venues'])} (deduped), cities {len(cities)}, "
          f"titles {len(titles)} ({sum(1 for t in titles if t['zh'])} with 中文), "
          f"posters {len(posters)}, productions {len(productions)} works -> data/venues_catalog.json")


if __name__ == "__main__":
    main()
