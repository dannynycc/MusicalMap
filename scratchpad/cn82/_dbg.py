import sys, io, json, os

_out = io.TextIOWrapper(open(sys.stdout.fileno(), "wb", closefd=False), encoding="utf-8")


def P(*a):
    _out.write(" ".join(str(x) for x in a) + "\n")
    _out.flush()


sys.path.insert(0, "scripts")
LANG = sys.argv[1]
IDX = int(sys.argv[2])
src = open("scripts/px_gen.py", encoding="utf-8").read()
head = src.split("SHOWS=json.load", 1)[0]
g = {"__name__": "__main__", "__file__": "scripts/px_gen.py"}
sys.argv = ["px_gen.py", LANG, "/dev/null", "x"]
exec(compile(head, "px_gen", "exec"), g)
suf = {"zh-hant": "zht", "en": "en"}[LANG]
lst = json.load(open("scratchpad/cn82/regen_%s_list.json" % suf, encoding="utf-8"))
order = json.load(open("scratchpad/cn82/regen_%s_order.json" % suf, encoding="utf-8"))
Q = lst[IDX] + g["TAIL"]
P("=== 組:", order[IDX], "| prompt 長度", len(Q), "| LO,HI =", g["LO"], g["HI"])
from playwright.sync_api import sync_playwright

with sync_playwright() as pw:
    b = pw.chromium.connect_over_cdp("http://127.0.0.1:9223")
    ctx = b.contexts[0]
    a = g["ask_once"](ctx, Q)
P("=== 回答長度", len(a))
P(a[:2000])
