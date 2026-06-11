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
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

DATA = Path(__file__).resolve().parent.parent / "data"


# Same production, differently branded across sources/regions — map to one key.
GROUP_ALIASES = {
    "mj the michael jackson": "mj",                 # Perth/TM long brand vs "MJ The Musical"
    "mj the michael jackson musical": "mj",
    "monty python s spamalot": "spamalot",
    "les mis": "les miserables",                    # broadway.org slug-style title
}


def group_key(title):
    """Canonical key so the same show titled differently across sources groups
    together (e.g. 'SIX' == 'SIX: The Musical', 'Mamma Mia!' == 'Mamma Mia',
    'Les Misérables' == 'Les Miserables'). Diacritics are stripped BEFORE the
    ascii filter, otherwise 'é' becomes a word break and spellings diverge."""
    t = re.sub(r"[–—]", "-", title or "")  # en/em-dash → '-' BEFORE ascii-strip drops them
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode()
    t = t.lower().strip()
    t = re.sub(r"^the\s+", "", t)
    t = re.sub(r"^disney(?:'s| presents)\s+", "", t)
    # any dash/colon marketing subtitle that mentions "musical", in any language
    # ("– Das Hit-Musical auf Schweizerdeutsch", ": The Broadway Musical", …)
    t = re.sub(r"\s*[:\-–—]\s*[^:]*musical.*$", "", t)
    t = re.sub(r"\s*[:\-–—]\s*(a\s+new\s+musical|the\s+musical|reimagined).*$", "", t)
    # trailing "…(the) Xxx Yyy Musical" brand tails without a dash
    t = re.sub(r"\s+(?:the\s+)?(?:[\w'!\-]+\s+){0,4}musical$", "", t)
    t = re.sub(r"[^a-z0-9]+", " ", t).strip()
    if not t:  # over-stripped (e.g. a title that IS just "…Musical") — fall back
        t = re.sub(r"[^a-z0-9]+", " ",
                   unicodedata.normalize("NFKD", title or "").encode("ascii", "ignore").decode().lower()).strip()
    return GROUP_ALIASES.get(t, t)

# Curated sources (precise data). Order matters for de-dup: later files win.
SOURCE_FILES = ["broadway.json", "westend.json", "tours.json", "intl.json", "manual.json"]
# Ticketmaster is added only for countries the curated sources DON'T cover,
# so it fills global gaps (Australia, NZ, Ireland, Nordics, Canada…) without
# duplicating the well-curated US/UK/etc. productions.
TM_FILE = "ticketmaster.json"


def country_norm(c):
    c = (c or "").lower()
    if "united states" in c or c == "usa":
        return "us"
    if "great britain" in c or "united kingdom" in c or c == "uk":
        return "gb"
    return c.strip()


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

    # Ticketmaster gap-fill: keep only countries curated sources don't cover.
    tm_path = DATA / TM_FILE
    if tm_path.exists():
        curated_countries = {country_norm(s.get("country")) for s in by_id.values()}
        tm = json.loads(tm_path.read_text(encoding="utf-8")).get("shows", [])
        kept = 0
        for s in tm:
            if country_norm(s.get("country")) in curated_countries:
                continue  # already covered by a curated source
            by_id[s["id"]] = s
            kept += 1
        print(f"  {TM_FILE}: +{kept} gap-fill ({len(tm)} total, "
              f"{len(tm) - kept} skipped as already-covered countries)")
        sources.append({"file": TM_FILE, "count": kept})

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
