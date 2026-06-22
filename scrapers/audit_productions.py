"""Audit the production (製作/版本) layer — catch broken posters & stale rules.

Checks:
  1. works.json `poster` / archival production `poster` → local file exists & is an image.
  2. archival productions in works.json with NO poster (so they fall back to work level).
  3. works whose `poster` is null/absent AND have no live shows (no thumbnail at all).
  4. catalog `productions`: live entries missing a poster URL.

Non-blocking — prints a report. Run: python scrapers/audit_productions.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

IMG_EXT = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif"}


def _is_local_image(poster):
    """For a posters/… local path: must exist and have an image extension.
    Returns (ok, reason). Remote http(s) posters are assumed checked by audit_images."""
    if not poster or poster.startswith("http"):
        return True, ""
    p = ROOT / poster
    if not p.exists():
        return False, "file missing"
    if p.suffix.lower() not in IMG_EXT:
        return False, f"not an image ext ({p.suffix})"
    return True, ""


def main():
    works = json.loads((DATA / "works.json").read_text(encoding="utf-8")).get("works", [])
    cat = json.loads((DATA / "venues_catalog.json").read_text(encoding="utf-8"))
    posters = cat.get("posters", {})
    cat_prods = cat.get("productions", {})

    broken, no_poster_arch, no_thumb, live_no_poster = [], [], [], []

    # group_key needs build_shows; import lazily so this still runs standalone-ish
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from build_shows import group_key

    for w in works:
        c = w["canonical"]
        g = group_key(c)
        wp = w.get("poster")
        ok, why = _is_local_image(wp if wp and wp != "auto" else None)
        if not ok:
            broken.append(f"{c} (work poster): {wp} — {why}")
        # work has no usable poster at all?
        has_work_poster = (wp and wp != "auto") or (g in posters)
        if not has_work_poster:
            no_thumb.append(c)
        for pr in (w.get("productions") or []):
            pp = pr.get("poster")
            ok, why = _is_local_image(pp)
            if not ok:
                broken.append(f"{c} → {pr.get('key')}: {pp} — {why}")
            if pr.get("origin") == "archival" and not pp:
                no_poster_arch.append(f"{c} → {pr.get('key')} ({pr.get('label')})")

    for g, arr in cat_prods.items():
        for pr in arr:
            if pr.get("origin") == "live" and not pr.get("poster"):
                live_no_poster.append(f"{g} → {pr.get('key')}")

    def section(title, items):
        print(f"\n{title}: {len(items)}")
        for it in items:
            print(f"  - {it}")

    print("=== production audit ===")
    print(f"works {len(works)}, works-with-productions {sum(1 for w in works if w.get('productions'))}, "
          f"catalog production-groups {len(cat_prods)}")
    section("❌ BROKEN posters (missing file / not image)", broken)
    section("⚠ archival productions with NO poster (falls back to work)", no_poster_arch)
    section("⚠ live productions missing a poster URL", live_no_poster)
    section("⚠ works with NO thumbnail at all (no poster, not playing)", no_thumb)
    print("\nDONE." + (" (broken posters found — fix before relying on them)" if broken else " all posters resolve."))


if __name__ == "__main__":
    main()
