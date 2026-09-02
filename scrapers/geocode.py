"""Venue geocoding with a persistent cache.

West End / Broadway theatres are a small, stable set, so we geocode each venue
once via OpenStreetMap Nominatim and cache the result forever in
data/venues.json keyed by a stable slug. Subsequent runs hit the cache and make
zero network calls. This keeps us off unreliable per-run geocoding and respects
Nominatim's usage policy (<=1 req/sec, descriptive User-Agent).
"""

import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"
CACHE_FILE = DATA / "venues.json"
USER_AGENT = "MusicalMap/0.1 (https://github.com/dannynycc; dannynycc@gmail.com)"

# Google Geocoding 只當【備援】:Nominatim 查得到就不會呼叫,所以既有結果一律不受影響。
# 2026-09-02 加。動機:Nominatim 對亞洲地方場館命中率很差 —— 實測
# 대전 상상아트홀 / 계명아트센터 / 부산북구문화예술회관 韓文英文都查無,
# 同一批 Google 是 7/7 全中,且世宗 Jochiwon 正確落在世宗市而不是首爾。
# 金鑰檔不存在時整段跳過,行為與加這段之前完全相同。
GKEY_FILE = Path(__file__).resolve().parent / ".gmaps_key"


def _gkey():
    try:
        return GKEY_FILE.read_text(encoding="utf-8").strip() or None
    except OSError:
        return None


def _load_cache():
    if CACHE_FILE.exists():
        return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
    return {}


def _save_cache(cache):
    CACHE_FILE.write_text(
        json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def _google(query):
    """Google Geocoding 備援。回傳 (lat, lng),查不到或出錯回 (None, None)。

    ⚠️ 這是要花錢的路徑,只在 Nominatim 失敗時走。額度與期限見 memory
    `project_musicalmap_place_ids`(試用額度到 2026-09-13,之後要回到節制模式)。
    """
    key = _gkey()
    if not key:
        return None, None
    url = "https://maps.googleapis.com/maps/api/geocode/json?" + urllib.parse.urlencode(
        {"address": query, "key": key, "language": "en"}
    )
    try:
        with urllib.request.urlopen(url, timeout=20) as r:
            d = json.loads(r.read().decode("utf-8"))
    except Exception as e:  # noqa: BLE001
        print(f"  [geocode/google] FAILED {query!r}: {e}")
        return None, None
    if d.get("status") != "OK" or not d.get("results"):
        # ZERO_RESULTS 是正常的「查不到」;其他狀態(OVER_QUERY_LIMIT /
        # REQUEST_DENIED)要印出來,否則額度用完會變成安靜的全面查無。
        if d.get("status") not in ("OK", "ZERO_RESULTS"):
            print(f"  [geocode/google] status={d.get('status')} {d.get('error_message','')}")
        return None, None
    loc = d["results"][0]["geometry"]["location"]
    return round(float(loc["lat"]), 6), round(float(loc["lng"]), 6)


def geocode(slug, query):
    """Return (lat, lng) for a venue, using cache first then Nominatim.

    slug:  stable cache key (e.g. "his-majestys-theatre|London")
    query: human query for Nominatim (e.g. "His Majesty's Theatre, London, UK")
    Returns (None, None) and caches the miss-free None if not found.
    """
    cache = _load_cache()
    if slug in cache:
        c = cache[slug]
        if c.get("lat") is not None:
            return c["lat"], c["lng"]
        # 命中的是【找不到】。舊快取是 Nominatim 單獨的結論,Google 還沒試過 ——
        # 給它一次機會,試過就記 src,之後不再重打(冪等,不會每跑一次燒一次額度)。
        if c.get("src") in ("google", "google-miss") or not _gkey():
            return None, None
        lat, lng = _google(query)
        cache[slug] = {"lat": lat, "lng": lng, "query": query,
                       "src": "google" if lat is not None else "google-miss"}
        _save_cache(cache)
        return lat, lng

    url = "https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode(
        {"q": query, "format": "json", "limit": 1}
    )
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    lat = lng = None
    src = "nominatim"
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            results = json.loads(r.read().decode("utf-8"))
        if results:
            lat = round(float(results[0]["lat"]), 6)
            lng = round(float(results[0]["lon"]), 6)
    except Exception as e:  # noqa: BLE001 — log and continue; a miss is non-fatal
        print(f"  [geocode] FAILED {query!r}: {e}")

    if lat is None and _gkey():          # 備援:Nominatim 查不到才打 Google
        lat, lng = _google(query)
        src = "google" if lat is not None else "google-miss"

    cache[slug] = {"lat": lat, "lng": lng, "query": query, "src": src}
    _save_cache(cache)
    time.sleep(1.1)  # Nominatim rate limit: max 1 request/second
    return lat, lng
