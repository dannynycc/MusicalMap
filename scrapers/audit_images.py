"""Image-quality audit: flag posters whose NATURAL size is smaller than what
the popup displays (height 340px), i.e. images that will look blurry.
Run after adding any source.  python scrapers/audit_images.py"""
import json, sys, io, urllib.request
from PIL import Image
from collections import defaultdict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
MIN_H = 340
d = json.load(open("data/shows.json", encoding="utf-8"))["shows"]
by_url = defaultdict(list)
for s in d:
    if s.get("image"):
        by_url[s["image"]].append(f"{s['source']}|{s['title'][:24]}")
print(f"{len(by_url)} distinct images")
bad, ok = [], 0
for u, srcs in by_url.items():
    try:
        req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
        raw = urllib.request.urlopen(req, timeout=25).read()
        im = Image.open(io.BytesIO(raw))
        if im.size[1] < MIN_H:
            bad.append((im.size, srcs[0], u))
        else:
            ok += 1
    except Exception as e:
        bad.append((("ERR", str(e)[:36]), srcs[0], u))
print(f"sharp(h>={MIN_H}): {ok} | blurry/err: {len(bad)}")
for size, src, u in sorted(bad, key=lambda x: str(x[1])):
    print(f"  {str(size):16s} {src:44s} {u[:80]}")
