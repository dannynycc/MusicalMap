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
    orphans = []
    for lang in LANGS:
        lib = json.load(io.open(os.path.join(LIB, "%s.json" % lang), encoding="utf-8"))
        syn = lib.get("syn", lib)
        served = {g: rec for g, rec in syn.items() if g in cat}
        total_lib += len(syn); total_served += len(served)
        if lang == "zh-hant":
            orphans = sorted(set(syn) - cat)
        out = dict(lib); out["syn"] = served
        json.dump(out, io.open(os.path.join(OUT, "%s.json" % lang), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=2)
    sys.stderr.write("[build_served_synopses] 庫 %d/語 → 前端 served %d/語(catalog %d)\n"
                     % (total_lib // 3, total_served // 3, len(cat)))
    warn_near_miss_orphans(orphans, cat)


def warn_near_miss_orphans(orphans, cat):
    """庫裡有、目錄沒有的鍵大多是【檔期已過】,那是正常的(庫本來就長期保存)。
    危險的是另一種:鍵【幾乎】等於某個目錄 group —— 那通常是【鍵打錯】,
    簡介明明備好了卻永遠送不出去,而這支腳本原本完全不會出聲。

    🚨 真實案例(2026-09-04):庫鍵『生命最美好的5分鍾』vs 目錄 group『生命最美好的5分鐘』——
       簡體「钟」還原成繁體時 鐘/鍾 二選一選錯,這齣台灣劇(苗北,11/13,檔期還沒到)
       的三語簡介一直沒被服務,而管線只印「庫 605 → served 527」,完全看不出異常。
    ⚠ 只告警不自動合併:同一輪掃描也撈到『テニスの王子様』vs『新テニスの王子様』,
       那是【兩部不同的作品】,合併就錯了。判斷交給人。
    """
    import difflib
    hits = []
    for g in orphans:
        near = difflib.get_close_matches(g, cat, n=1, cutoff=0.85)
        if near and near[0] != g:
            hits.append((g, near[0]))
    if hits:
        sys.stderr.write("::warning::庫裡有 %d 個鍵【極接近但不等於】某個 catalog group,"
                         "可能是鍵打錯導致簡介永遠送不出去(也可能是不同作品,請人工判斷):\n" % len(hits))
        for g, n in hits:
            sys.stderr.write("::warning::  庫 %r  ↔  目錄 %r\n" % (g, n))

if __name__ == "__main__":
    main()
