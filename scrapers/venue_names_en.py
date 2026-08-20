"""替「只有中日韓文名、我們手上沒有英文名」的場館,用 Google Places 補官方英文名。

背景:英文站的場館名走 gen_variants.mjs 的 fallback 鏈(venues_en.json 精確表 →
cn_venues.json 權威表 → venues_catalog.json 名稱/座標 → 字串內的英文段)。2026-08-20
盤點後仍有 93 種純中日韓館名在英文站露出中文,其中一部分在 venues_catalog.json 裡
有 place_id —— place_id 查 Places Details 並指定 languageCode=en,拿得到官方英文名。

寫進 data/venues_en.json(鏈的第一站,gen_variants 不必改)。

安全規則(使用者的 Google 試用額度,實測約 NT$0.11/次):
  * 只查「還沒有英文名」且「目錄有 place_id」的場館,查過就寫檔,不重查。
  * MAX_CALLS 硬上限,超過直接中止。
  * 回傳如果還是中日韓文(Google 對某些場館就是沒有英文名),**不寫入**,保持原樣不亂造。

KEY: 環境變數 GOOGLE_MAPS_KEY,否則讀 scrapers/.gmaps_key(已 gitignore)。

用法:
  python -u scrapers/venue_names_en.py --dry     # 只列出會查哪些,不呼叫 API
  python -u scrapers/venue_names_en.py           # 實際查並寫入
"""

import io
import json
import math
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
DETAILS = "https://places.googleapis.com/v1/places/"
MAX_CALLS = 120          # 硬上限:每家最多兩次查詢(當地名驗證 + 英文名)
CJK = re.compile(r"[぀-ヿ㐀-鿿가-힯豈-﫿]")


def latin(v):
    s = " ".join(x for x in str(v or "").split() if not CJK.search(x)).strip()
    return re.sub(r"[\s/,\-–—]+$", "", s).strip()


def main_en(v):
    return re.sub(r"\s*\([^)]*\)\s*$", "", latin(v)).strip().lower()


def dist_m(a, b, c, d):
    R, p = 6371008.8, math.pi / 180
    h = (0.5 - math.cos((c - a) * p) / 2
         + math.cos(a * p) * math.cos(c * p) * (1 - math.cos((d - b) * p)) / 2)
    return 2 * R * math.asin(math.sqrt(h))


def load_key():
    k = os.environ.get("GOOGLE_MAPS_KEY")
    if k:
        return k.strip()
    f = ROOT / "scrapers" / ".gmaps_key"
    if f.exists():
        return f.read_text(encoding="utf-8").strip()
    print("找不到金鑰(GOOGLE_MAPS_KEY 或 scrapers/.gmaps_key)", file=sys.stderr)
    sys.exit(2)


def pid_for(venue, rows, cat_all, cat_geo):
    """沿用 gen_variants 的判定順序:名稱證據優先,座標只在不含糊時採用。"""
    zh = " ".join(x for x in venue.split() if CJK.search(x)).strip()
    hit = None
    if zh:
        hit = next((c for c in cat_all if c.get("search") and zh in str(c["search"])), None) \
            or next((c for c in cat_all if c.get("name") and zh in str(c["name"])), None)
    if hit and hit.get("pid"):
        return hit["pid"], "名稱"
    s = next((x for x in rows if x.get("venue") == venue
              and isinstance(x.get("lat"), (int, float))), None)
    if not s:
        return None, "沒座標"
    near = [c for c in cat_geo if dist_m(s["lat"], s["lng"], c["lat"], c["lng"]) <= 40]
    pids = {c["pid"] for c in near if c.get("pid")}
    if len(pids) == 1:
        return pids.pop(), "座標"
    return None, f"40m 內有 {len(pids)} 個 place_id,不猜"


def _details(pid, key, lang=None):
    url = DETAILS + urllib.parse.quote(pid) + ("?languageCode=" + lang if lang else "")
    req = urllib.request.Request(
        url, headers={"X-Goog-Api-Key": key, "X-Goog-FieldMask": "displayName"})
    try:
        r = json.loads(urllib.request.urlopen(req, timeout=25).read())
    except urllib.error.HTTPError as e:
        return None, f"HTTP {e.code}: " + e.read().decode("utf-8", "ignore")[:160]
    except Exception as exc:
        return None, str(exc)[:120]
    return ((r.get("displayName") or {}).get("text") or "").strip(), None


def _core(v):
    """比對用:去標點空白與常見廳別後綴,只留主名。"""
    s = re.sub(r"[\s·・\-–—_()（）\[\]【】,，.。:：/]+", "", str(v or ""))
    for suf in ("大劇院", "大剧院", "中劇院", "中剧院", "小劇場", "小剧场", "大劇場", "大剧场",
                "歌劇廳", "歌剧厅", "音樂廳", "音乐厅", "演藝廳", "演艺厅", "演奏廳", "演奏厅",
                "多功能廳", "多功能厅", "劇場", "剧场", "劇院", "剧院", "廳", "厅"):
        if s.endswith(suf) and len(s) > len(suf) + 1:
            s = s[: -len(suf)]
    return s


# 驗證用的當地語言:不指定 languageCode 時 Places 回的是**英文**,拿英文跟中文館名比
# 當然永遠不中(2026-08-20 第一版就是這樣全軍覆沒),所以要依國別明確指定。
LOCAL_LANG = {"Taiwan": "zh-TW", "Hong Kong": "zh-HK", "Macau": "zh-TW",
              "China": "zh-CN", "Japan": "ja", "South Korea": "ko"}
GENERIC_EN = {"venue", "theatre", "theater", "hall", "center", "centre", "arena", "studio"}


def fetch_en(pid, key, venue, country):
    """先用**當地語言**的名字驗這個 place_id 到底是不是同一家,再取英文名。

    目錄裡的 place_id 有些指到整棟商場或旁邊的地標,直接信英文名會寫出離譜的東西
    (實測:「星空间·星空穹顶剧场」→ Shanghai Astronomy Museum、
    「桑塔露琪亚·广州馆」→ Guangzhou Museum of Art)。所以多花一次查詢,
    要求 Google 的當地名與我們的館名**主名互為包含**,否則整筆丟掉、不寫入。"""
    local, err = _details(pid, key, LOCAL_LANG.get(country, "zh-CN"))
    if err:
        return None, err
    a, b = _core(venue), _core(local)
    if not b or not (a in b or b in a):
        return None, f"place_id 指向別的地方(當地名:{local!r}),不採用"
    en, err = _details(pid, key, "en")
    if err:
        return None, err
    if en and en.strip().lower() in GENERIC_EN:
        return None, f"英文名太籠統({en!r}),不採用"
    return en, None


def main():
    dry = "--dry" in sys.argv
    shows = json.loads((DATA / "shows.json").read_text(encoding="utf-8"))
    rows = shows["shows"] if isinstance(shows, dict) and "shows" in shows else shows
    cat = json.loads((DATA / "venues_catalog.json").read_text(encoding="utf-8"))
    cat_all = cat.get("venues") or []
    cat_geo = [v for v in cat_all if isinstance(v.get("lat"), (int, float))]
    ven_en = json.loads((DATA / "venues_en.json").read_text(encoding="utf-8"))

    country_of = {}
    for s in rows:
        v = (s.get("venue") or "").strip()
        if v and v not in country_of and s.get("country"):
            country_of[v] = s["country"]
    targets = sorted({(s.get("venue") or "").strip() for s in rows
                      if s.get("venue") and CJK.search(s["venue"])
                      and not latin(s["venue"]) and s["venue"] not in ven_en})
    print(f"沒有英文名的中日韓館名:{len(targets)} 種")

    todo = []
    for v in targets:
        pid, why = pid_for(v, rows, cat_all, cat_geo)
        if pid:
            todo.append((v, pid, why))
    print(f"其中目錄有 place_id、可以查的:{len(todo)} 種\n")
    for v, _, why in todo:
        print(f"   [{why}] {v}")
    if dry:
        print("\n--dry:沒有呼叫 API。")
        return
    if len(todo) > MAX_CALLS:
        print(f"要查 {len(todo)} 家,超過硬上限 {MAX_CALLS},中止。")
        sys.exit(1)

    key = load_key()
    added, skipped, failed = 0, [], []
    for i, (v, pid, _) in enumerate(todo, 1):
        name, err = fetch_en(pid, key, v, country_of.get(v, ""))
        if err:
            failed.append((v, err))
            print(f"  {i}/{len(todo)} ✗ {v}: {err}")
            time.sleep(0.2)
            continue
        if not name or CJK.search(name):
            skipped.append((v, name))
            print(f"  {i}/{len(todo)} — {v}: Google 也沒有英文名({name!r}),不寫入")
        else:
            ven_en[v] = name
            added += 1
            print(f"  {i}/{len(todo)} ✓ {v}  →  {name}")
        time.sleep(0.2)

    if added:
        (DATA / "venues_en.json").write_text(
            json.dumps(ven_en, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"\n查了 {len(todo)} 家:寫入 {added}、Google 也沒英文名 {len(skipped)}、失敗 {len(failed)}")
    print(f"venues_en.json 現在 {len(ven_en)} 筆")


if __name__ == "__main__":
    import urllib.parse  # noqa: E402  (只在需要組 URL 時用到)
    main()
