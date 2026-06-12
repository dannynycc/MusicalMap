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
import sys
import io
import urllib.request
from datetime import datetime, timezone, timedelta

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from pathlib import Path
DATA = Path(__file__).resolve().parent.parent / "data"
API = "https://search.opentix.life/search"

# non-musicals that nonetheless carry the 戲劇-音樂劇 tag (user-flagged); substring match
EXCLUDE = ["老闆", "陽春麵", "演唱會"]   # plays / concerts mis-tagged as 音樂劇 (user-flagged)
TW_TZ = timezone(timedelta(hours=8))


def fetch():
    body = json.dumps({"language": "zh-CHT", "categoryFilter": ["戲劇-音樂劇"],
                       "sortBy": "ABOUT_TO_BEGIN"}).encode("utf-8")
    req = urllib.request.Request(API, data=body, method="POST", headers={
        "Content-Type": "application/json", "Origin": "https://www.opentix.life",
        "Referer": "https://www.opentix.life/", "User-Agent": "MusicalMap/0.1"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def ymd(ms):
    if not ms:
        return None
    return datetime.fromtimestamp(ms / 1000, TW_TZ).strftime("%Y-%m-%d")


def main():
    data = fetch()
    found = (data.get("result") or {}).get("found", [])
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
        v = (s.get("eventVenues") or [{}])[0]
        loc = v.get("location") or {}
        try:
            lat, lng = round(float(loc["lat"]), 6), round(float(loc["lon"]), 6)
        except (KeyError, TypeError, ValueError):
            dropped.append(zh_title + " (無座標)"); continue
        times = v.get("times") or []
        starts = [t.get("start") for t in times if t.get("start")]
        ends = [t.get("end") for t in times if t.get("end")]
        start = ymd(min(starts)) if starts else ymd(s.get("startDateTime"))
        end = ymd(max(ends)) if ends else ymd(s.get("endDateTime"))
        if end and end < today:                      # already finished
            dropped.append(zh_title + " (已結束)"); continue
        pid = s.get("id")
        shows.append({
            "id": "opentix-" + str(pid),
            "title": zh_title or en_title,        # Taiwanese productions are known by their 中文 title
            "title_en": en_title,
            "venue": v.get("name", ""), "city": v.get("city", ""), "country": "Taiwan",
            "lat": lat, "lng": lng, "start_date": start, "end_date": end,
            "image": s.get("imageUrl"),
            "ticket_url": f"https://www.opentix.life/program/{pid}" if pid else None,
            "type": "tour", "verified": True, "source": "opentix.life",
        })
    out = {"meta": {"source": "opentix.life", "count": len(shows)}, "shows": shows}
    (DATA / "opentix.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  kept {len(shows)}, dropped {len(dropped)}", flush=True)
    for d in dropped:
        print("    drop:", d, flush=True)
    print(f"Wrote {len(shows)} -> data/opentix.json", flush=True)


if __name__ == "__main__":
    main()
