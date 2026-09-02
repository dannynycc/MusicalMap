# -*- coding: utf-8 -*-
"""簡介正文裡的「裸標題」掃描器。

症狀:Perplexity 偶爾把「Themes」「主題」「全劇總結」這類小標【單獨成段】印進正文中間。
px_gen 的尾段守衛只砍結尾(while paras[-1] 不以句末標點結束就 pop),砍不到夾在段落【中間】的,
所以會一路寫進知識庫。2026-09-02 實測:西葡第二批英文前 16 篇有 2 篇中招,
先驗批次的 germans de sang 也中過 —— 不是偶發,是 clean() 的一個漏掉的變型。

判準:單行、長度 < 40、且結尾不是句末標點的段落。正文成段絕不會長這樣。
(這個判準有鑑別力:掃描前先確認過確實抓得到已知的中招案例,不是恆真檢查。)

用法:
  python scripts/qa/scan_bare_headings.py                 # 掃知識庫,只報告
  python scripts/qa/scan_bare_headings.py --fix           # 掃知識庫並就地修掉
  python scripts/qa/scan_bare_headings.py <file.json> ... # 另掃指定的生成結果檔([{show,synopsis}])
"""
import sys, io, os, json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

END_OK = "。.!?！？”\"’'）)】」』…"
LIB = "data/synopses_library"
SUBS = {"en": ["en"], "zh-hant": ["zh"], "zh-hans": ["zh-hans"]}


def bare_headings(text):
    """回傳這篇裡所有的裸標題段落。"""
    if not text:
        return []
    out = []
    for p in [x.strip() for x in text.split("\n\n")]:
        if p and "\n" not in p and len(p) < 40 and p[-1] not in END_OK:
            out.append(p)
    return out


def strip_bare_headings(text):
    paras = [x.strip() for x in text.split("\n\n") if x.strip()]
    keep = [p for p in paras
            if not ("\n" not in p and len(p) < 40 and p[-1] not in END_OK)]
    return "\n\n".join(keep)


def scan_library(fix):
    total = hits = 0
    for lang, subs in SUBS.items():
        path = os.path.join(LIB, "%s.json" % lang)
        if not os.path.exists(path):
            continue
        doc = json.load(io.open(path, encoding="utf-8"))
        syn = doc.get("syn", {})
        changed = 0
        for group, entry in syn.items():
            for sub in subs:
                text = (entry or {}).get(sub)
                if not text:
                    continue
                total += 1
                found = bare_headings(text)
                if not found:
                    continue
                hits += 1
                print("  [%s] %-42s -> %s" % (lang, group[:42], " | ".join(found)))
                if fix:
                    entry[sub] = strip_bare_headings(text)
                    changed += 1
        if fix and changed:
            json.dump(doc, io.open(path, "w", encoding="utf-8"),
                      ensure_ascii=False, indent=1)
            print("  == %s 已修 %d 篇 ==" % (lang, changed))
    print("知識庫:掃描 %d 篇,發現 %d 篇有裸標題%s"
          % (total, hits, "(已修)" if fix else ""))
    return hits


def scan_results(paths):
    hits = 0
    for path in paths:
        rows = json.load(io.open(path, encoding="utf-8"))
        for row in rows:
            found = bare_headings(row.get("synopsis", ""))
            if found:
                hits += 1
                print("  [%s] %-42s -> %s"
                      % (os.path.basename(path), row.get("show", "")[:42],
                         " | ".join(found)))
    print("生成結果檔:發現 %d 篇有裸標題" % hits)
    return hits


def main():
    args = [a for a in sys.argv[1:] if a != "--fix"]
    fix = "--fix" in sys.argv
    hits = scan_results(args) if args else scan_library(fix)
    sys.exit(1 if (hits and not fix) else 0)


main()
