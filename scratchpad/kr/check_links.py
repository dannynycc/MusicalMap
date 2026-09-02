# -*- coding: utf-8 -*-
"""把 interpark.json 的每一條購票連結真的打一次。抽驗過≠全部過。"""
import io, json, sys, time, urllib.request, urllib.error
from collections import Counter
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/128.0"}
d = json.load(io.open("data/interpark.json", encoding="utf-8"))["shows"]
bad, c = [], Counter()
for i, r in enumerate(d, 1):
    u = r["ticket_url"]
    try:
        s = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=20).status
    except urllib.error.HTTPError as e:
        s = e.code
    except Exception as e:                                   # noqa: BLE001
        s = str(e)[:20]
    c[s] += 1
    if s != 200:
        bad.append((r["title"][:40], u, s))
    if i % 25 == 0:
        print("  ...%d/%d" % (i, len(d)))
    time.sleep(0.25)
print("\n狀態碼分布:", dict(c))
print("非 200 的:", len(bad))
for b in bad:
    print("   ", b)
