# -*- coding: utf-8 -*-
"""音樂劇知識庫歸檔:把生成的簡介結果併入後台知識庫 data/synopses_library/<lang>.json
(前端 data/synopses/ 由 build_served_synopses.py 從庫過濾產生,不直接寫),
key 一律用爬蟲同一套 build_shows.group_key(),確保「不在庫」的劇日後有製作出現時
卡片能自動掛上(group 吻合)。對 app 無害:只在 group 對到卡片時才顯示。

用法: python scripts/kb_merge.py <en|zh-hant|zh-hans> <results.json> [--title-field show] [--syn-field synopsis]
results.json = [{"show": <劇名>, "synopsis": <內文>}, ...]
狀態寫到 scripts/kb_merge.last.log(不用 stdout,因 build_shows import 時會重設 stdout)。
"""
import sys, io, json, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scrapers"))
sys.path.insert(0, "scrapers")
import build_shows as bs  # 注意:import 會重設 stdout

LANG = sys.argv[1]
RESULTS = sys.argv[2]
KEYMAP_FILE = sys.argv[3] if len(sys.argv) > 3 and not sys.argv[3].startswith("--") else None
SUB = {"en": "en", "zh-hant": "zh", "zh-hans": "zh-hans"}[LANG]
DATA = "data/synopses_library/%s.json" % LANG
LOG = os.path.join(os.path.dirname(__file__), "kb_merge.last.log")

def log(msg):
    with io.open(LOG, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

def main():
    gen = json.load(io.open(RESULTS, encoding="utf-8"))
    # keymap: 在庫的劇用「已知 DB group」;檔案格式 [[group, title], ...] 或 {title: group}
    keymap = {}
    if KEYMAP_FILE and os.path.exists(KEYMAP_FILE):
        km = json.load(io.open(KEYMAP_FILE, encoding="utf-8"))
        if isinstance(km, dict):
            keymap = km
        else:
            for g, t in km:
                keymap[t] = g
    d = json.load(io.open(DATA, encoding="utf-8"))
    syn = d["syn"]
    before = len(syn)
    added = 0; updated = 0; keymap = []
    for r in gen:
        title = r.get("show") or r.get("title")
        text = r.get("synopsis") or r.get("text")
        if not title or not text:
            continue
        key = keymap.get(title) or bs.group_key(title)
        rec = syn.setdefault(key, {})
        if SUB in rec:
            updated += 1
        else:
            added += 1
        rec[SUB] = text
        keymap.append("%s -> %s" % (title, key))
    json.dump(d, io.open(DATA, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    log("=== kb_merge %s: %d 筆輸入; group 新增 %d, 覆蓋 %d; 庫從 %d -> %d ===" %
        (LANG, len(gen), added, updated, before, len(syn)))
    for k in keymap:
        log("   " + k)

if __name__ == "__main__":
    io.open(LOG, "w", encoding="utf-8").close()  # 清空 log
    main()
