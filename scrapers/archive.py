"""Accumulating, immutable historical archive of musical RUNS.

The live pipeline (scrapers -> build_shows -> shows.json) is a pure snapshot of
what's on sale now/soon; it OVERWRITES daily, so closed shows vanish forever. This
script is a SEPARATE, stateful layer that never throws history away:

    archive = previous archive  ∪  today's shows.json

Design invariants (see the architecture discussion):
  * FACTS are immutable. Once a run has closed (end_date well in the past) its
    title / venue / city / dates are frozen and never rewritten by a later scrape.
  * DERIVED values are NOT frozen. group + tag are recomputed every run from the
    current works.json registry, so improving the classifier retroactively fixes
    history's display — without ever touching the recorded facts/dates.
  * Identity is a stable NATURAL KEY (group | city | venue | start-year), not the
    volatile per-source id, so the same run merges across days and sources.
  * Auto-accumulated runs (provenance="auto") and hand-curated deep-history runs
    (data/curated_history.json, provenance="curated") share one schema; curated
    facts always win and are never overwritten by a scrape.

Output: data/archive/<year>.json  (+ data/archive/index.json)
Run daily in CI AFTER build_shows.py. Seed the past once with bootstrap_archive.py.
"""

import json
import hashlib
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Reuse the live pipeline's normalisation + classifier so identity and tags match
# exactly what the map shows. (Importing functions only; build_shows.main() is
# guarded by __main__ so nothing runs on import. build_shows also sets utf-8 stdout
# on import, so we don't re-wrap here — re-wrapping orphans+GC-closes the buffer.)
from build_shows import group_key, classify_tag, city_key

DATA = Path(__file__).resolve().parent.parent / "data"
ARCHIVE_DIR = DATA / "archive"
FREEZE_GRACE_DAYS = 21   # a run is frozen this long after its end_date (allow late date fixes)

# Fields that are FACTS (frozen once closed). Everything else (group/tag) is derived.
FACT_FIELDS = ("title", "venue", "city", "country", "lat", "lng",
               "start_date", "end_date", "image", "ticket_url", "source", "type")


def run_key(group, city, venue, start_date):
    """Stable identity for one production-run: same show + city + venue + start
    YEAR. Revivals in different years are distinct; a continuous sit-down run keeps
    one key across daily scrapes. Touring stops differ by venue/city."""
    yr = (start_date or "")[:4]
    raw = f"{group}|{city_key(city)}|{(venue or '').strip().lower()}|{yr}"
    return "run-" + hashlib.sha1(raw.encode("utf-8")).hexdigest()[:12]


def _facts_from_show(s, as_of):
    return {
        "title": s.get("title"), "venue": s.get("venue"), "city": s.get("city"),
        "country": s.get("country"), "lat": s.get("lat"), "lng": s.get("lng"),
        "start_date": s.get("start_date"), "end_date": s.get("end_date"),
        "image": s.get("image"), "ticket_url": s.get("ticket_url"),
        "source": s.get("source"), "type": s.get("type"),
        "onsale_only": s.get("onsale_only", False),
        "provenance": "auto", "first_seen": as_of, "last_seen": as_of, "frozen": False,
    }


def merge_snapshot(archive, shows, as_of):
    """Fold one day's shows into the archive (in place). `as_of` = the snapshot's
    date (YYYY-MM-DD) — today for the daily run, the commit date when bootstrapping
    from git so first_seen/freeze reflect when we actually observed each run."""
    for s in shows:
        g = s.get("group") or group_key(s.get("title", ""))
        rid = run_key(g, s.get("city"), s.get("venue"), s.get("start_date"))
        rec = archive.get(rid)
        if rec is None:
            archive[rid] = {"run_key": rid, **_facts_from_show(s, as_of)}
        elif not rec.get("frozen") and rec.get("provenance") == "auto":
            rec["last_seen"] = as_of
            # widen the observed window; never shrink it
            for key, cmp in (("start_date", min), ("end_date", max)):
                a, b = rec.get(key), s.get(key)
                rec[key] = cmp(a, b) if a and b else (a or b)
            # refresh volatile display facts while the run is still live
            for f in ("image", "ticket_url", "lat", "lng", "venue", "city"):
                if s.get(f):
                    rec[f] = s[f]


def finalize(archive, today):
    """Freeze runs whose end_date is comfortably past, and (re)derive group + tag
    for EVERY record from current rules — facts stay put, display stays current."""
    cutoff = (datetime.strptime(today, "%Y-%m-%d") - timedelta(days=FREEZE_GRACE_DAYS)).strftime("%Y-%m-%d")
    for rec in archive.values():
        end = rec.get("end_date")
        if rec.get("provenance") == "auto" and end and end < cutoff:
            rec["frozen"] = True
        rec["group"] = group_key(rec.get("title", ""))
        rec["tag"] = classify_tag(rec["group"], rec.get("source"), rec.get("country"))
        rec["status"] = ("upcoming" if (rec.get("start_date") or "") > today
                         else "closed" if end and end < today else "running")


def load_archive():
    archive = {}
    if ARCHIVE_DIR.exists():
        for f in sorted(ARCHIVE_DIR.glob("[0-9][0-9][0-9][0-9].json")):
            for rec in json.loads(f.read_text(encoding="utf-8")).get("runs", []):
                archive[rec["run_key"]] = rec
    return archive


def load_curated(archive, as_of):
    """Merge hand-curated deep-history runs. Curated facts are authoritative and
    never overwritten by auto-accumulation (curated key wins)."""
    path = DATA / "curated_history.json"
    if not path.exists():
        return
    for c in json.loads(path.read_text(encoding="utf-8")).get("runs", []):
        g = group_key(c.get("title", ""))
        rid = c.get("run_key") or run_key(g, c.get("city"), c.get("venue"), c.get("start_date"))
        archive[rid] = {
            "run_key": rid, "provenance": "curated", "frozen": True,
            "first_seen": c.get("first_seen", as_of), "last_seen": as_of,
            "onsale_only": False,
            **{f: c.get(f) for f in FACT_FIELDS},
        }


def save_archive(archive, today):
    ARCHIVE_DIR.mkdir(exist_ok=True)
    by_year = {}
    today_y = int(today[:4])

    def sane_year(v):
        try:
            y = int((v or "")[:4])
            return y if 1980 <= y <= today_y + 5 else None
        except ValueError:
            return None

    # 跨年展開(2026-07-14 深稽核):舊制「只放 start 年檔」讓 Phantom(1988~2023)
    # 只躺在 1988.json——前端過去視圖只載「視圖年±1」,看 2020 年根本載不到它,
    # 所有跨年長跑劇在過去視圖整批消失。改為 run 檔期覆蓋的每一年都放一份
    # (仍在演的 end=null 展到今年);單筆記錄小,重複成本可忽略。
    # 年份 sanity:teatromadrid 曾解析出 1229-02-23,把 index earliest 打到 1229、
    # 時間軸滑桿撐到近萬格——出範圍的年不採計,回落 end 年/首見年。
    for rec in archive.values():
        y0 = sane_year(rec.get("start_date"))
        y1 = sane_year(rec.get("end_date"))
        if y0 is None and y1 is None:
            y0 = y1 = sane_year(rec.get("first_seen")) or today_y
        elif y0 is None:
            y0 = y1
        elif y1 is None:
            # end 缺:closed=資料殘缺只放 start 年;running/upcoming=演到現在
            y1 = today_y if rec.get("status") in ("running", "upcoming") else y0
        for yr in range(min(y0, y1), max(y0, y1) + 1):
            by_year.setdefault(str(yr), []).append(rec)
    # rewrite every year file (cheap; keeps them sorted/clean)
    for f in ARCHIVE_DIR.glob("[0-9][0-9][0-9][0-9].json"):
        f.unlink()
    index = {"_comment": "Per-year historical run archive. Load index, then the "
             "year file(s) the user browses. Facts are frozen once closed; group/tag "
             "are re-derived each build.", "generated_at": today, "years": {}}
    for yr, runs in sorted(by_year.items()):
        runs.sort(key=lambda r: (r.get("start_date") or "", r.get("title") or ""))
        (ARCHIVE_DIR / f"{yr}.json").write_text(
            json.dumps({"year": yr, "count": len(runs), "runs": runs},
                       ensure_ascii=False, indent=2), encoding="utf-8")
        index["years"][yr] = len(runs)
    index["total"] = sum(index["years"].values())
    (ARCHIVE_DIR / "index.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
    return index


def main():
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    archive = load_archive()
    before = len(archive)
    shows = json.loads((DATA / "shows.json").read_text(encoding="utf-8")).get("shows", [])
    merge_snapshot(archive, shows, today)
    load_curated(archive, today)
    finalize(archive, today)
    index = save_archive(archive, today)
    frozen = sum(1 for r in archive.values() if r.get("frozen"))
    print(f"archive: {before} -> {len(archive)} runs (+{len(archive)-before} new), "
          f"{frozen} frozen, {index['total']} across {len(index['years'])} year(s) "
          f"-> data/archive/")


if __name__ == "__main__":
    main()
