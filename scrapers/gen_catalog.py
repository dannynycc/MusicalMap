"""Generate data/venues_catalog.json — autocomplete dictionary for the personal
"log a musical" form (venues, cities, bilingual titles, currencies, posters).

Run: python scrapers/gen_catalog.py
"""

import html as htmllib
import json
import re
import sys
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
DATA = Path(__file__).resolve().parent.parent / "data"

# Curated venues missing from the musical dataset (name, city, country, lat, lng)
CURATED = [
    ("National Theater (國家戲劇院)", "Taipei", "Taiwan", 25.0360, 121.5168),
    ("National Concert Hall (國家音樂廳)", "Taipei", "Taiwan", 25.0349, 121.5167),
    ("Taipei Performing Arts Center (臺北表演藝術中心)", "Taipei", "Taiwan", 25.0578, 121.5256),
    ("National Taichung Theater (臺中國家歌劇院)", "Taichung", "Taiwan", 24.1631, 120.6406),
    ("Weiwuying (衛武營國家藝術文化中心)", "Kaohsiung", "Taiwan", 22.6045, 120.3349),
    ("Taipei Arena (臺北小巨蛋)", "Taipei", "Taiwan", 25.0515, 121.5510),
    ("Hong Kong Cultural Centre", "Hong Kong", "Hong Kong", 22.2940, 114.1700),
    ("Esplanade Theatre", "Singapore", "Singapore", 1.2897, 103.8559),
    ("Sands Theatre, Marina Bay Sands", "Singapore", "Singapore", 1.2847, 103.8590),
    ("Tokyu Theatre Orb (東急シアターオーブ)", "Tokyo", "Japan", 35.6590, 139.7036),
    ("Imperial Theatre (帝国劇場)", "Tokyo", "Japan", 35.6759, 139.7626),
    ("Nissay Theatre (日生劇場)", "Tokyo", "Japan", 35.6736, 139.7616),
    ("Seoul Arts Center (예술의전당)", "Seoul", "South Korea", 37.4786, 127.0119),
    ("Sejong Center (세종문화회관)", "Seoul", "South Korea", 37.5725, 126.9760),
    ("Sydney Opera House", "Sydney", "Australia", -33.8568, 151.2153),
    ("Théâtre du Châtelet", "Paris", "France", 48.8576, 2.3470),
    ("Teatro alla Scala", "Milan", "Italy", 45.4674, 9.1895),
    ("Raimund Theater", "Vienna", "Austria", 48.1969, 16.3438),
    ("Ronacher", "Vienna", "Austria", 48.2073, 16.3760),
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
}

CURRENCIES = ["TWD 新台幣", "USD 美元", "GBP 英鎊", "EUR 歐元", "JPY 日圓",
              "KRW 韓元", "CNY 人民幣", "HKD 港幣", "SGD 新幣", "AUD 澳幣",
              "CAD 加幣", "CHF 瑞郎", "CZK 捷克克朗", "MXN 墨西哥披索"]


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


def main():
    shows = json.loads((DATA / "shows.json").read_text(encoding="utf-8"))["shows"]

    # venues — dedup by (normalized name, city); keep the longest/cleanest display
    vmerge = {}
    def add_venue(name, city, country, lat, lng):
        if not name or lat is None:
            return
        name = re.sub(r"\s{2,}", " ", htmllib.unescape(name)).strip()  # fix &#039; / &amp;
        city = (city or "").strip()
        nk = norm_venue(name, city)
        if not nk:
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

    cities = sorted({(s.get("city"), s.get("country") or "") for s in shows if s.get("city")})

    # bilingual titles + poster per show-group
    groups, posters = {}, {}
    for s in shows:
        g = s.get("group") or s["title"].lower()
        groups.setdefault(g, s["title"])
        if s.get("image") and g not in posters:
            posters[g] = s["image"]
    titles = []
    for g, en in sorted(groups.items(), key=lambda x: x[1].lower()):
        zh = ZH.get(re.sub(r"[^a-z0-9 ]", "", g).strip())
        titles.append({"en": en, "zh": zh, "group": g})

    out = {
        "venues": sorted(vmerge.values(), key=lambda v: v["name"]),
        "cities": [{"city": c, "country": k} for c, k in cities],
        "titles": titles,
        "currencies": CURRENCIES,
        "posters": posters,   # group_key -> poster url, for map cards
    }
    (DATA / "venues_catalog.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"venues {len(out['venues'])} (deduped), cities {len(cities)}, "
          f"titles {len(titles)} ({sum(1 for t in titles if t['zh'])} with 中文), "
          f"posters {len(posters)} -> data/venues_catalog.json")


if __name__ == "__main__":
    main()
