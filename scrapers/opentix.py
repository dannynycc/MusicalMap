"""Taiwan musicals via OPENTIX (兩廳院售票系統) — the authoritative TW source.

OPENTIX is a SPA; its search is a JSON API:
  POST https://search.opentix.life/search
  body {"language":"zh-CHT","categoryFilter":["戲劇-音樂劇"],"sortBy":"ABOUT_TO_BEGIN"}
Each result has title / englishTitle / eventVenues[{name, city, location, times}] /
imageUrl / id, so we get real venue + coords (WGS-84) + run dates + poster.

We keep category 戲劇-音樂劇 but DROP choir galas (also tagged 音樂-合唱, e.g. the
竹科媽媽 series) and a small manual exclude list of non-musicals the user flagged.

Output: data/opentix.json   Run: python scrapers/opentix.py
"""

import json
import re
import sys
import io
import urllib.request
from datetime import datetime, timezone, timedelta

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from pathlib import Path
DATA = Path(__file__).resolve().parent.parent / "data"
API = "https://search.opentix.life/search"

# non-musicals that nonetheless carry the 戲劇-音樂劇 tag (user-flagged); substring match
# OPENTIX 戲劇-音樂劇 is organiser-tagged and noisy. Drop by title:
#  (a) non-musical type words (舞台劇 play, 擊樂秀 percussion show, 漫才 manzai comedy,
#      演唱會/音樂會 concert, 工作坊 workshop), and
#  (b) specific user-flagged mis-tagged shows (plays / talks / fringe pieces).
EXCLUDE = ["演唱會", "音樂會", "工作坊", "舞台劇", "擊樂秀", "漫才",
           "老闆", "陽春麵", "一粒萬倍", "H&G2",
           "怪美妖仙傳", "一個彥達", "最後五秒", "築夢之橋", "天堂客棧"]
TW_TZ = timezone(timedelta(hours=8))

# OPENTIX returns Chinese city names; map to English so they align with the curated
# tw_venues.json cities (else the same hall appears twice — Chinese-city vs English-city).
CITY_MAP = {
    "臺北": "Taipei", "台北": "Taipei", "新北": "New Taipei", "基隆": "Keelung",
    "桃園": "Taoyuan", "新竹": "Hsinchu", "苗栗": "Miaoli", "臺中": "Taichung", "台中": "Taichung",
    "彰化": "Changhua", "南投": "Nantou", "雲林": "Yunlin", "嘉義": "Chiayi",
    "臺南": "Tainan", "台南": "Tainan", "高雄": "Kaohsiung", "屏東": "Pingtung",
    "宜蘭": "Yilan", "花蓮": "Hualien", "臺東": "Taitung", "台東": "Taitung",
    "澎湖": "Penghu", "金門": "Kinmen", "連江": "Lienchiang", "馬祖": "Lienchiang",
}


def fetch():
    """All 戲劇-音樂劇 programs. The API returns only 15 per page (hitsCount is the
    real total) + a nextOffset cursor — page through it or far-future shows like
    囍宴 (Sept) get dropped."""
    items, offset, hits = [], 0, None
    while True:
        body = json.dumps({"language": "zh-CHT", "categoryFilter": ["戲劇-音樂劇"],
                           "sortBy": "ABOUT_TO_BEGIN", "offset": offset}).encode("utf-8")
        req = urllib.request.Request(API, data=body, method="POST", headers={
            "Content-Type": "application/json", "Origin": "https://www.opentix.life",
            "Referer": "https://www.opentix.life/", "User-Agent": "MusicalMap/0.1"})
        with urllib.request.urlopen(req, timeout=30) as r:
            res = (json.loads(r.read().decode("utf-8")).get("result") or {})
        page = res.get("found", [])
        items.extend(page)
        hits = res.get("hitsCount", hits)
        nxt = res.get("nextOffset")
        if not page or nxt is None or nxt <= offset or (hits and len(items) >= hits):
            break
        offset = nxt
    return items


def ymd(ms):
    if not ms:
        return None
    return datetime.fromtimestamp(ms / 1000, TW_TZ).strftime("%Y-%m-%d")


def tag_hint(raw):
    """從『外框標記』讀作品的起源傳統(core_title 會把它洗掉,classify 就再也看不到):
    「韓國音樂劇《如蝶翩翩》」「百老匯授權音樂劇《Honk!》」——先於 core_title 判讀,
    輸出 build_shows classify_tag 認得的 tradition;無標記回 None(照舊走 fallback)。
    2026-07-09 資料品質稽核:如蝶翩翩/6點下班/月亮雪酪/Honk 全因此誤標「台灣」。"""
    t = raw or ""
    # 中英標記都讀(caller 應傳 zh_title+' '+en_title;英文顯示題名也可能帶 Korean/Broadway 等標記)
    if re.search(r"韓國|韩国|Korean?\b", t, re.I): return "韓國原創"
    if re.search(r"百老匯|西區|倫敦|London|Broadway|West\s*End", t, re.I): return "Broadway/West End"
    if re.search(r"日本|寶塚|宝塚|2\.5次元|Japanese|Takarazuka", t, re.I): return "日本原創"
    if re.search(r"法文|法語|法國音樂劇|French\s+musical", t, re.I): return "法式音樂劇"
    if re.search(r"德語|德文|維也納|German\s+musical|Vienna", t, re.I): return "德奧音樂劇"
    return None


def core_title(t):
    """Organisers wrap the real show name in 《》 with festival/company/marketing
    text around it — '《幸福三姐妹》音樂劇' / '果陀劇場《生命中最美好的5分鐘》2026音樂奇蹟重現'.
    Pull out the bracketed name; if there's no 《》 but a type word ('…音樂劇 囍宴'),
    take the part after it; otherwise return the raw title."""
    t = (t or "").strip()
    m = re.search(r"[《＜](.+?)[》＞]", t)              # 《》 is the canonical title bracket
    if m:
        return m.group(1).strip()
    m = re.search(r"[「『](.+?)[」』]", t)              # else the name may sit in 「」/『』
    if m:
        return m.group(1).strip()
    m = re.search(r"(?:音樂劇|歌舞劇|舞台劇)[\s:：]+(.+)$", t)
    if m:
        return m.group(1).strip()
    return t


def main():
    found = fetch()
    print(f"  OPENTIX returned {len(found)} 戲劇-音樂劇 programs", flush=True)
    today = datetime.now(TW_TZ).strftime("%Y-%m-%d")
    shows, dropped = [], []
    for f in found:
        s = f.get("source") or {}
        zh_title = (s.get("title") or "").strip()    # OPENTIX display title (Taiwanese audiences know it by this)
        en_title = (s.get("englishTitle") or "").strip()
        cats = s.get("categories") or []
        if "音樂-合唱" in cats:                      # choir gala, not a musical
            dropped.append(zh_title + " (合唱)"); continue
        if any(x in zh_title for x in EXCLUDE):
            dropped.append(zh_title + " (排除)"); continue
        pid = s.get("id")
        # A program can tour several venues (e.g. 勸世三姊妹: 國家戲劇院/臺中/衛武營) —
        # each eventVenue carries its OWN coords + session times, so emit one per venue.
        venues = s.get("eventVenues") or []
        kept_any = False
        for vi, v in enumerate(venues):
            loc = v.get("location") or {}
            try:
                lat, lng = round(float(loc["lat"]), 6), round(float(loc["lon"]), 6)
            except (KeyError, TypeError, ValueError):
                continue
            times = v.get("times") or []
            starts = [t.get("start") for t in times if t.get("start")]
            ends = [t.get("end") for t in times if t.get("end")]
            start = ymd(min(starts)) if starts else ymd(s.get("startDateTime"))
            end = ymd(max(ends)) if ends else ymd(s.get("endDateTime"))
            if end and end < today:                  # this stop already finished
                continue
            kept_any = True
            rec = {
                "id": f"opentix-{pid}-{vi}",
                "title": core_title(zh_title) or en_title,   # real show name, festival/company wrapper stripped
                "title_en": en_title,
                "venue": v.get("name", ""), "city": CITY_MAP.get(v.get("city", ""), v.get("city", "")), "country": "Taiwan",
                "lat": lat, "lng": lng, "start_date": start, "end_date": end,
                "image": s.get("imageUrl"),
                "ticket_url": f"https://www.opentix.life/program/{pid}" if pid else None,
                "type": "tour", "verified": True, "source": "opentix.life",
            }
            th = tag_hint(zh_title + " " + en_title)   # 外框標記(韓國/百老匯授權…)在洗標題前先判讀;中英題名都讀
            if th:
                rec["tag_hint"] = th
            shows.append(rec)
        if not kept_any:
            dropped.append(zh_title + " (無未來場次/座標)")
    out = {"meta": {"source": "opentix.life", "count": len(shows)}, "shows": shows}
    (DATA / "opentix.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  kept {len(shows)}, dropped {len(dropped)}", flush=True)
    for d in dropped:
        print("    drop:", d, flush=True)
    print(f"Wrote {len(shows)} -> data/opentix.json", flush=True)


if __name__ == "__main__":
    main()
