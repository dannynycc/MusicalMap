"""Automatic external-API call accounting for the scrapers.

Importing this module monkey-patches ``urllib.request.urlopen`` (every scraper uses the
qualified ``urllib.request.urlopen(...)`` form, so a single patch covers them all) to:
  * tally HTTP calls per host, and
  * capture any ``Rate-Limit*`` response headers (e.g. Ticketmaster's daily quota).

On process exit it merges this process's tallies into ``logs/api_usage.json`` under the
current CI run (``GITHUB_RUN_ID``, or local date+hour), so over a few runs we can see the
total API load per host — and judge whether there's headroom to scrape more often.

Wired in via ``scrapers/_run.py`` (the CI runs each scraper through it), so NO scraper
file needs editing. Strictly best-effort: it must never raise into the caller, and a
failure here must never break a scrape.
"""

import atexit
import json
import os
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

_LOG = Path(__file__).resolve().parent.parent / "logs" / "api_usage.json"
_MAX_RUNS = 120                 # bounded ring buffer of recent runs
_tally = {}                     # host -> {calls, [quota, available, over]}
_orig_urlopen = urllib.request.urlopen


def _host(arg):
    try:
        url = arg.full_url if isinstance(arg, urllib.request.Request) else str(arg)
        return urllib.parse.urlparse(url).netloc or "?"
    except Exception:
        return "?"


def _counted_urlopen(arg, *args, **kwargs):
    host = _host(arg)
    t = _tally.setdefault(host, {"calls": 0})
    t["calls"] += 1                              # count attempts (failed calls still hit quota)
    resp = _orig_urlopen(arg, *args, **kwargs)
    try:
        h = resp.headers
        if h.get("Rate-Limit"):                  # APIs that expose a quota (e.g. Ticketmaster)
            t["quota"] = int(h.get("Rate-Limit"))
            t["available"] = int(h.get("Rate-Limit-Available"))
            t["over"] = int(h.get("Rate-Limit-Over") or 0)
    except Exception:
        pass
    return resp


urllib.request.urlopen = _counted_urlopen        # the one-line patch that covers every scraper


def _run_key():
    return os.environ.get("GITHUB_RUN_ID") or datetime.now(timezone.utc).strftime("local-%Y-%m-%dT%H")


@atexit.register
def _flush():
    if not _tally:
        return
    try:
        _LOG.parent.mkdir(parents=True, exist_ok=True)
        data = {"runs": []}
        if _LOG.exists():
            try:
                data = json.loads(_LOG.read_text(encoding="utf-8"))
            except Exception:
                data = {"runs": []}
        runs = data.setdefault("runs", [])
        key = _run_key()
        entry = next((r for r in runs if r.get("run") == key), None)
        if entry is None:
            entry = {"run": key,
                     "started_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                     "hosts": {}}
            runs.append(entry)
        for host, t in _tally.items():
            h = entry["hosts"].setdefault(host, {"calls": 0})
            h["calls"] += t["calls"]
            for f in ("quota", "available", "over"):
                if f in t:
                    h[f] = t[f]
        entry["updated_utc"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        entry["total_calls"] = sum(h["calls"] for h in entry["hosts"].values())
        data["runs"] = runs[-_MAX_RUNS:]
        _LOG.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass                                      # telemetry must never break a scrape
