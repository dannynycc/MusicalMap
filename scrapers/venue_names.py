"""Bilingual names for Asian (CJK / Korean / Japanese) venues via Google Places.

For venues in countries whose names aren't Latin script, fetch BOTH the English
name and the local-language name, so the catalog can show "English 原文" and let
users search in either script. Western venues are left as-is (already Latin).

Writes data/venue_names.json: "venue|city" -> {"en": ..., "native": ...}
KEY: env GOOGLE_MAPS_KEY or scrapers/.gmaps_key (gitignored).
Run: python -u scrapers/venue_names.py   (incremental; --all to redo)
"""

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

# reuse the Google client + key loader from geocode_google
# (its import sets up UTF-8 stdout, so we don't re-wrap it here)
import importlib.util
_spec = importlib.util.spec_from_file_location("gg", ROOT / "scrapers" / "geocode_google.py")
gg = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(gg)

# country -> local-language code for the native place name
LOCALE = {
    "Taiwan": "zh-TW", "China": "zh-CN", "Hong Kong": "zh-HK", "Macau": "zh-HK",
    "Singapore": "zh-SG", "Japan": "ja", "South Korea": "ko",
}


def is_ascii(s):
    return all(ord(ch) < 128 for ch in (s or ""))


def place_name(query, key, lang):
    r = gg.places_new(query, key, language=lang)
    if isinstance(r, tuple) and r and r[0] != "DENIED" and len(r) >= 3:
        return r[2]
    return None


def main():
    key = gg.load_key()
    force = "--all" in sys.argv
    out_path = DATA / "venue_names.json"
    existing = json.loads(out_path.read_text(encoding="utf-8")) if out_path.exists() else {}

    shows = json.loads((DATA / "shows.json").read_text(encoding="utf-8"))["shows"]
    todo = {}
    for s in shows:
        co = s.get("country")
        v, c = s.get("venue"), s.get("city")
        if co in LOCALE and v and (v, c) not in todo:
            k = gg.vkey(v, c)
            if force or k not in existing:
                todo[(v, c)] = (co, k)

    if not todo:
        print("No new Asian venues to name (all present). --all to redo.", flush=True)
        return
    print(f"naming {len(todo)} Asian venues (en + native)", flush=True)
    names = dict(existing)
    for i, ((v, c), (co, k)) in enumerate(sorted(todo.items()), 1):
        q = f"{v}, {c}, {co}"
        en = v if is_ascii(v) else place_name(q, key, "en")
        time.sleep(0.06)
        native = place_name(q, key, LOCALE[co])     # local-language name
        time.sleep(0.06)
        # keep only a genuinely different native form
        if native and en and native.strip() == en.strip():
            native = ""
        names[k] = {"en": (en or v), "native": (native or "")}
        print(f"  [{i}/{len(todo)}] {v} → en='{names[k]['en']}' native='{names[k]['native']}'", flush=True)

    out_path.write_text(json.dumps(names, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nDONE: {len(names)} venue names -> data/venue_names.json", flush=True)


if __name__ == "__main__":
    main()
