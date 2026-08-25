# -*- coding: utf-8 -*-
"""前端交付過濾:把後台完整知識庫(data/synopses_library/)過濾成「只含目前在庫(catalog)的劇」
寫到 data/synopses/(瀏覽器實際抓的檔)。後台庫可無限長到上千部,前端檔恆定只含在庫的劇。
每日 CI 在 gen_catalog 之後跑這支,新上演的劇就自動掛上早已備好的簡介。

Fail-safe:catalog group 數異常少(<100)時「絕不覆蓋」前端檔(避免爬蟲當天全掛時把簡介清空)。
用法: python scripts/build_served_synopses.py
"""
import json, io, os, sys

LIB = "data/synopses_library"
OUT = "data/synopses"
LANGS = ["en", "zh-hant", "zh-hans"]

def catalog_groups():
    d = json.load(io.open("data/variants/shows.en.json", encoding="utf-8"))
    shows = d.get("shows", d)
    return set((s.get("group") or "").lower() for s in shows if (s.get("group") or ""))

def main():
    cat = catalog_groups()
    if len(cat) < 100:
        sys.stderr.write("[build_served_synopses] catalog group 數僅 %d,疑似異常,拒絕覆蓋前端檔\n" % len(cat))
        sys.exit(2)
    total_served = 0; total_lib = 0
    for lang in LANGS:
        lib = json.load(io.open(os.path.join(LIB, "%s.json" % lang), encoding="utf-8"))
        syn = lib.get("syn", lib)
        served = {g: rec for g, rec in syn.items() if g in cat}
        total_lib += len(syn); total_served += len(served)
        out = dict(lib); out["syn"] = served
        json.dump(out, io.open(os.path.join(OUT, "%s.json" % lang), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=2)
    sys.stderr.write("[build_served_synopses] 庫 %d/語 → 前端 served %d/語(catalog %d)\n"
                     % (total_lib // 3, total_served // 3, len(cat)))

if __name__ == "__main__":
    main()
