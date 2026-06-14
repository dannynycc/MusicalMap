"""One-off: seed data/archive/ from git history.

CI has been committing data/shows.json daily, so git ALREADY holds an immutable,
timestamped snapshot for every past build. This walks those commits oldest->newest
and folds each historical shows.json into the archive exactly as the daily archiver
would have — giving us retroactive history for free, back to the first commit.

Run once (from repo root):  python scrapers/bootstrap_archive.py

CAVEAT: this backfills snapshots AS THEY WERE LISTED — including shows that a later
clean-up has since removed (e.g. non-musicals that passed an older, weaker filter),
and identities computed under whatever normalisation those commits used. So if the
classifier/normalisation has changed materially, prefer the clean forward path:
delete data/archive/ and run archive.py once against the CURRENT shows.json, then
let the daily CI accumulate from there. Forward accumulation — not this backfill —
is the source of truth.
"""

import json
import subprocess
from datetime import datetime, timezone

import archive as A   # reuse merge/freeze/save logic (also sets utf-8 stdout on import)


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True,
                          encoding="utf-8").stdout


def main():
    # commits that touched shows.json, oldest first: "<hash> <iso-date>"
    log = git("log", "--reverse", "--format=%H %cI", "--", "data/shows.json")
    commits = [ln.split(" ", 1) for ln in log.splitlines() if ln.strip()]
    print(f"found {len(commits)} historical shows.json commit(s) in git")

    arch = {}            # start fresh; bootstrap is the source of truth for the past
    seen_dates = set()
    for h, iso in commits:
        day = iso[:10]
        if day in seen_dates:
            continue     # one snapshot per day is plenty (overlapsMonth needs no finer)
        seen_dates.add(day)
        blob = git("show", f"{h}:data/shows.json")
        if not blob.strip():
            continue
        try:
            shows = json.loads(blob).get("shows", [])
        except json.JSONDecodeError:
            continue
        A.merge_snapshot(arch, shows, day)
        print(f"  {day}: folded {len(shows)} shows -> {len(arch)} cumulative runs")

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    A.load_curated(arch, today)
    A.finalize(arch, today)
    index = A.save_archive(arch, today)
    print(f"\nbootstrapped {index['total']} runs across {len(index['years'])} year(s) "
          f"from {len(seen_dates)} daily snapshot(s) -> data/archive/")


if __name__ == "__main__":
    main()
