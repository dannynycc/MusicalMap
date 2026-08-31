# -*- coding: utf-8 -*-
"""簡介殘留掃描器(SOP §5「每次 merge 後必重掃殘留」的落地版)。

抓兩類 Perplexity 產物殘留:
  1. 總結段落被加上標題行(「全劇總結」/「全剧总结」/「Summary」等)——正文不該有小標。
  2. 來源 slug 殘留:整行只有一個小寫 latin token(mtishows / broadwayworld …)或裸網域。

用法:
    python scripts/scan_synopsis_artifacts.py            # 只掃描報告(預設)
    python scripts/scan_synopsis_artifacts.py --fix      # 就地修掉標題行,再報告剩下的

library 與 served 兩邊都掃/都修(SOP:改 served 一定要同步回 library,否則下次
build_served 會用舊 library 蓋掉修正)。
"""
import json, io, os, re, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILES = [("synopses_library", "en", "en"), ("synopses_library", "zh-hant", "zh"),
         ("synopses_library", "zh-hans", "zh-hans"),
         ("synopses", "en", "en"), ("synopses", "zh-hant", "zh"),
         ("synopses", "zh-hans", "zh-hans")]

# 獨立成行的「總結」小標(正文絕不會這樣寫)
HEADING = re.compile(
    r"(?m)^[ \t　]*(全劇總結|全剧总结|本劇總結|本剧总结|劇情總結|剧情总结|總結|总结|"
    r"Summary|SUMMARY|Overall Summary|Conclusion)[ \t　]*[:：]?[ \t　]*$")
# 來源 slug:整行單一小寫 latin token,或裸網域。
# 長度放寬到 2 字元起(px_gen 的 clean() 用 {3,},會漏掉 "hdk"、"nfi" 這種三字母劇院縮寫)——
# 正文成段絕不會只有一行小寫 latin 短詞。
SLUG = re.compile(r"(?m)^[ \t]*([a-z][a-z0-9\-]{1,}|[a-z0-9.\-]+\.[a-z]{2,})[ \t]*$")

MARK = ""   # 控制字元當 sentinel:正文不可能出現(別用私用區 U+E000,那是雙重編碼損毀的指紋)


def strip_heading(text):
    """刪掉獨立的小標行,並把它留下的空段落收乾淨。"""
    out = HEADING.sub(MARK, text)
    if MARK not in out:
        return text, 0
    n = out.count(MARK)
    out = re.sub(r"\n*" + MARK + r"\n*", "\n\n", out)
    return re.sub(r"\n{3,}", "\n\n", out).strip(), n


def main():
    fix = "--fix" in sys.argv
    total_head = total_slug = total_fixed = 0
    for kind, fname, sub in FILES:
        path = os.path.join(ROOT, "data", kind, fname + ".json")
        doc = json.load(open(path, encoding="utf-8"))
        syn = doc["syn"]
        heads, slugs, fixed = [], [], 0
        for g, v in syn.items():
            text = (v.get(sub) if isinstance(v, dict) else v) or ""
            if not text:
                continue
            if HEADING.search(text):
                heads.append(g)
                if fix:
                    new, _ = strip_heading(text)
                    if new != text:
                        if isinstance(v, dict):
                            v[sub] = new
                        else:
                            syn[g] = new
                        fixed += 1
            if SLUG.search(text):
                slugs.append(g)
        if fix and fixed:
            json.dump(doc, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        total_head += len(heads); total_slug += len(slugs); total_fixed += fixed
        print(f"{kind}/{fname}: 標題殘留 {len(heads)}" + (f" (已修 {fixed})" if fix else "") +
              f" | slug 殘留 {len(slugs)}")
        for g in heads[:8]:
            print("   . 標題:", g)
        for g in slugs[:8]:
            print("   . slug:", g)
    print(f"\n合計 標題殘留 {total_head} / slug 殘留 {total_slug}" +
          (f" / 已修 {total_fixed}" if fix else ""))
    return 1 if (total_head or total_slug) and not fix else 0


if __name__ == "__main__":
    sys.exit(main())
