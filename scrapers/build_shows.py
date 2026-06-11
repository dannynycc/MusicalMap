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
from datetime import datetime, timezone
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

DATA = Path(__file__).resolve().parent.parent / "data"


def group_key(title):
    """Canonical key so the same show titled differently across sources groups
    together (e.g. 'SIX' == 'SIX: The Musical', 'Mamma Mia!' == 'Mamma Mia').
    Conservative: only strips leading 'the' and trailing musical/subtitle tags."""
    t = (title or "").lower().strip()
    t = re.sub(r"^the\s+", "", t)
    t = re.sub(r"\s*[:\-–—]\s*(a\s+new\s+musical|the\s+musical|reimagined).*$", "", t)
    t = re.sub(r"\s+(the\s+musical|a\s+new\s+musical)$", "", t)
    t = re.sub(r"[^a-z0-9]+", " ", t).strip()
    return t

# Order matters for de-dup: later files override earlier ids.
SOURCE_FILES = ["broadway.json", "westend.json", "tours.json"]


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
            by_id[s["id"]] = s
        sources.append({"file": name, "count": len(rows), "meta": blob.get("meta", {})})
        print(f"  {name}: {len(rows)} shows")

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

    shows = list(by_id.values())

    # assign grouping key (same show across sources / locations)
    for s in shows:
        s["group"] = group_key(s["title"])

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
