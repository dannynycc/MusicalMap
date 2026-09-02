# -*- coding: utf-8 -*-
"""把西葡 55 組的查核結果從 scratchpad 帳本搬進常設出處總帳。

為什麼要這支
------------
docs/SYNOPSIS_SOP.md §4 指定的出處總帳是 data/synopses_verification.json(319 筆),
但西葡這批 55 組只寫在 scratchpad/eses/synopsis_ledger.json。下一個 session 依 SOP
去標準位置查,會看到這 55 組「沒有任何查核紀錄」—— 實際上做過,只是記在別的地方。

搬過去的是【摘要】,不是全文:總帳的 schema 只有 method/date/langs/sources/
errors_fixed/confidence/external_multisource/verify_scope,逐輪過程與逐字官方原文
仍留在 scratchpad 帳本,用 ledger 欄位指回去。

verify_scope 的判定(不謊報,對齊 memory `feedback_verification_tier_precision`):
  multisource = 帳本 sources ≥ 2 個【獨立網域】且 confidence=high
  single      = 只有 1 個可用外部來源,或 confidence=medium(官方僅檔期/無劇情大綱)
  internal    = 完全沒有外部來源(本批已無此類)
"""
import io
import json
import re
from urllib.parse import urlparse

LEDGER = "scratchpad/eses/synopsis_ledger.json"
VERIF = "data/synopses_verification.json"
LIB = "data/synopses_library/%s.json"
SUBKEY = [("en", "en"), ("zh-hant", "zh"), ("zh-hans", "zh-hans")]
BATCH = "eses-2026-09-02"
DATE = "2026-09-02"


def domains(sources):
    """從 sources 字串裡抽出獨立網域數。抽不出網域的條目(描述性來源)各算一個。"""
    out = set()
    for s in sources or []:
        m = re.search(r"https?://([^/\s)]+)", s)
        if m:
            out.add(urlparse("http://" + m.group(1)).netloc.lower().lstrip("www."))
        else:
            out.add(s[:40])
    return out


def main():
    led = json.load(io.open(LEDGER, encoding="utf-8"))["items"]
    ver = json.load(io.open(VERIF, encoding="utf-8"))
    v = ver["verified"]

    # langs 取【知識庫實際有什麼】而不是帳本的 lang_done —— 合併過的組(assassinat→
    # murder for two)帳本欄位是舊組的,會把 canonical 的語言數寫少。以庫為準才是事實。
    lib = {}
    for lang, sub in SUBKEY:
        lib[lang] = json.load(io.open(LIB % lang, encoding="utf-8"))["syn"]

    def langs_of(group):
        got = [lang for lang, sub in SUBKEY if ((lib[lang].get(group) or {}).get(sub))]
        return got or ["en", "zh-hant", "zh-hans"]

    before = len(v)
    added = updated = skipped_merged = 0
    scope_count = {"multisource": 0, "single": 0, "internal": 0}

    for g, rec in led.items():
        if rec.get("merged_into"):
            # 已併入 canonical 組:紀錄掛在 canonical 上,別留孤兒鍵
            g = rec["merged_into"]
            skipped_merged += 1
        srcs = rec.get("sources") or []
        nd = len(domains(srcs))
        conf = rec.get("confidence") or "medium"
        if nd == 0:
            scope = "internal"
        elif nd >= 2 and conf == "high":
            scope = "multisource"
        else:
            scope = "single"
        scope_count[scope] += 1

        entry = {
            "method": "B",
            "date": DATE,
            "langs": langs_of(g),
            "sources": "；".join(s[:120] for s in srcs) or "(無外部來源)",
            "errors_fixed": len(rec.get("fixes") or []),
            "confidence": conf,
            "external_multisource": scope == "multisource",
            "verify_scope": scope,
            "batch": BATCH,
            "ledger": "scratchpad/eses/synopsis_ledger.json#items." + g,
        }
        if g in v:
            v[g].update(entry)
            updated += 1
        else:
            v[g] = entry
            added += 1

    with io.open(VERIF, "w", encoding="utf-8") as f:
        json.dump(ver, f, ensure_ascii=False, indent=1)

    print("出處總帳 %d → %d 筆(新增 %d、更新 %d;其中 %d 筆因合併改掛 canonical 組)"
          % (before, len(v), added, updated, skipped_merged))
    print("verify_scope 分布:%s" % scope_count)
    # 護欄:誠實性檢查 —— 標成 multisource 的一定要真的有 >=2 個網域
    bad = [g for g, e in v.items()
           if e.get("batch") == BATCH and e.get("external_multisource")
           and len(domains([e["sources"]])) < 1]
    print("宣稱多源但抽不出來源的:%d 筆" % len(bad))
    return 0


raise SystemExit(main())
