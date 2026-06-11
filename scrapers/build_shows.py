"""Merge all per-source data files into data/shows.json (what the frontend reads).

Each source file is {"meta": {...}, "shows": [...]}. We concatenate, de-dup by
id (last source wins), and stamp combined meta. Keeping sources separate means a
re-scrape of one source never clobbers the others.

Run:  python scrapers/build_shows.py
"""

import json
import sys
import io
from datetime import datetime, timezone
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

DATA = Path(__file__).resolve().parent.parent / "data"

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

    shows = list(by_id.values())
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
