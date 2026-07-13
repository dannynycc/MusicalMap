"""標題健檢稽核(2026-07-13,Love Never Dies 未歸組事故後制度化)。

三個角度找「標題品質」問題,輸出清單供 CI 警告(exit 1 = 有新發現):
1. 未歸組嫌疑:某 group 的標題 token 是「已登錄作品」的嚴格超集(冠名/副標黏著,
   如 Andrew Lloyd Webber's LOVE NEVER DIES - The Phantom Returns ⊃ Love Never Dies)。
2. 同劇分裂嫌疑:兩個 group 標題 token 一方包含另一方且差 ≤3 詞。
3. 髒指紋:presents/starring/引號/tickets 尾/™ 等殘留。

天然誤報存在(Rocky Horror Show ⊃ Rocky),已確認為不同作品者列入 KNOWN_DISTINCT
白名單——審過一次就不再吵;新出現的才報。
"""
import json
import re
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
DATA = Path(__file__).resolve().parent.parent / "data"

# 已人工確認「確實是不同作品/合法標題」的配對與 group(2026-07-13 全站首掃逐筆判讀)。
# 格式:frozenset({較長標題的 group, 較短/作品名 的 group 或 canonical 小寫})
KNOWN_DISTINCT = {
    frozenset({"masquerade phantom of the opera reimagined", "the phantom of the opera"}),
    frozenset({"the rocky horror show", "rocky"}),
    frozenset({"weihnachten mit bibi tina das musical", "tina"}),
    frozenset({"tina the rock show experience", "tina"}),          # 待查:疑 tribute,查證前不歸組
    frozenset({"wah show temporada 6", "6點下班"}),
    frozenset({"reve cabaret", "cabaret"}),
    frozenset({"paris varsovie le cabaret musical ewunia", "cabaret"}),
    frozenset({"bear grease", "grease"}),
    frozenset({"oliver twist", "oliver!"}),
    frozenset({"el mago de oz", "oz"}),
    frozenset({"the wizard of oz", "oz"}),
    frozenset({"wild about you", "wild wild"}),
    frozenset({"million dollar quartet christmas", "million dollar quartet"}),
    frozenset({"despres de nosaltres grec", "despres de nosaltres"}),
    frozenset({"ballant ballant 30 anys", "くぼたまこと画業30周年記念 実写版 天体戦士サンレッドショー"}),
    frozenset({"daniel in the lions den featuring the story of esther", "daniel in the lions den featuring the story of esther"}),
}

_STOP = {"the", "a", "an", "of", "and", "le", "les", "la", "de", "musical", "on", "in",
         "das", "der", "die", "el", "il"}


def toks(t):
    t = unicodedata.normalize("NFKD", t or "").encode("ascii", "ignore").decode()
    return frozenset(re.findall(r"[a-z0-9]+", t.lower())) - _STOP


def norm_g(t):
    t = unicodedata.normalize("NFKD", t or "").encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9一-鿿 ]", " ", t.lower())).strip() or (t or "").lower()


_KNOWN_NORM = None


def known(a, b):
    global _KNOWN_NORM
    if _KNOWN_NORM is None:   # 白名單條目與比對值過同一個 norm(2026-07-13 首跑修正)
        _KNOWN_NORM = {frozenset(norm_g(x) for x in pair) for pair in KNOWN_DISTINCT}
    return frozenset({norm_g(a), norm_g(b)}) in _KNOWN_NORM


DIRTY = re.compile(r"\bpresents?\b|\bstarring\b|\btickets?$|^['\"“]|['\"”]$|\bpresented by\b|™|®", re.I)


def main():
    shows = json.loads((DATA / "shows.json").read_text(encoding="utf-8"))["shows"]
    works = json.loads((DATA / "works.json").read_text(encoding="utf-8"))["works"]
    groups = defaultdict(list)
    for s in shows:
        groups[s.get("group") or s["title"]].append(s)
    bad = []

    wtoks = {w["canonical"]: toks(w["canonical"]) for w in works if toks(w["canonical"])}
    for g, items in groups.items():
        gt = toks(items[0]["title"])
        for cn, wt in wtoks.items():
            if wt < gt and len(gt - wt) <= 4 and not known(items[0]["title"], cn):
                bad.append(f"未歸組嫌疑: {items[0]['title']!r} ⊃ work {cn!r} ({items[0].get('city')})")

    gl = [(g, toks(items[0]["title"]), items[0]) for g, items in groups.items()]
    for i, (g1, t1, s1) in enumerate(gl):
        for g2, t2, s2 in gl[i + 1:]:
            small, big = (t1, t2) if len(t1) < len(t2) else (t2, t1)
            sa, sb = (s1, s2) if len(t1) < len(t2) else (s2, s1)
            if small and small < big and len(big - small) <= 3 and not known(sa["title"], sb["title"]):
                bad.append(f"同劇分裂嫌疑: {sb['title']!r} ({sb.get('city')}) ⊃ {sa['title']!r} ({sa.get('city')})")

    for g, items in groups.items():
        t = items[0]["title"]
        if DIRTY.search(t):
            bad.append(f"髒指紋: {t!r} ({items[0].get('venue')}, {items[0].get('city')})")

    if bad:
        print(f"標題健檢:{len(bad)} 筆新發現(確認為不同作品請加 KNOWN_DISTINCT)")
        for b in sorted(set(bad)):
            print("  " + b)
        sys.exit(1)
    print("標題健檢 PASS(未歸組 0/分裂 0/髒指紋 0,白名單外)")


if __name__ == "__main__":
    main()
