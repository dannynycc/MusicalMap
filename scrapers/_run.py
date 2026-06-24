"""Run a scraper with automatic API-usage accounting.

Usage:  python scrapers/_run.py scrapers/<scraper>.py [args...]

It imports ``usage`` first (which patches urllib to count API calls per host and flush
to logs/api_usage.json on exit), then executes the target scraper exactly as if it were
run directly — same __main__ guard, same __file__, same argv. This keeps every scraper
unmodified while giving us per-run API load numbers. See scrapers/usage.py.
"""

import runpy
import sys

try:
    import usage  # noqa: F401  — installs the urlopen counter + atexit flush on import
except Exception as e:                            # never let instrumentation block a scrape
    print(f"_run: usage instrumentation unavailable ({e})", file=sys.stderr)

if len(sys.argv) < 2:
    print("usage: python scrapers/_run.py <script.py> [args...]", file=sys.stderr)
    sys.exit(2)

target = sys.argv[1]
sys.argv = sys.argv[1:]                           # target sees itself as argv[0], its args after
runpy.run_path(target, run_name="__main__")
