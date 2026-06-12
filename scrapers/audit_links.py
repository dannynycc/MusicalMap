"""Ticket-link audit: GET every distinct ticket_url (browser UA, redirects
followed) and report dead links. Some SPAs serve HTTP 404 to bots but render
fine in browsers (world.nol.com) — those hosts are checked but flagged
separately, not as dead.  python scrapers/audit_links.py"""
import json, sys, io, urllib.request, urllib.error
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
# Hosts returning error statuses to bots but rendering fine in real browsers
# (verified via playwright: Ticketmaster serves the full page with HTTP 401).
SOFT404_HOSTS = ("world.nol.com", "ticketmaster.", "ticketweb.")
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
      "Accept-Language": "en"}
d = json.load(open("data/shows.json", encoding="utf-8"))["shows"]
urls = defaultdict(list)
for s in d:
    for u in {s.get("ticket_url")} | {l.get("url") for l in (s.get("ticket_links") or [])}:
        if u:
            urls[u].append(f"{s['source']}|{s['title'][:24]}|{s['city']}")
def check(u):
    try:
        req = urllib.request.Request(u, headers=UA)
        r = urllib.request.urlopen(req, timeout=25)
        return u, r.status
    except urllib.error.HTTPError as e:
        return u, e.code
    except Exception as e:
        return u, str(e)[:40]
print(f"{len(urls)} distinct ticket urls")
with ThreadPoolExecutor(max_workers=12) as ex:
    results = list(ex.map(check, urls))
dead, soft, blocked, ok = [], [], [], 0
for u, st in results:
    if st == 200: ok += 1
    elif any(h in u for h in SOFT404_HOSTS): soft.append((st, u))
    elif st in (403, 429) or isinstance(st, str): blocked.append((st, u))
    else: dead.append((st, u))
print(f"ok:{ok}  DEAD:{len(dead)}  bot-blocked(403/err,需人工抽查):{len(blocked)}  SPA-soft404:{len(soft)}")
for st, u in sorted(dead, key=lambda x: x[1]):
    print(f"  DEAD {st} {u[:95]}  <- {urls[u][0]}")
for st, u in blocked[:10]:
    print(f"  BLOCKED {st} {u[:95]}")
