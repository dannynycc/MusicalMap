"""tour_name 可信度稽核(2026-07-13,Lexington/Arena Spectacular 事故後建)。

卡片大標顯示 tour_name,它錯=掛羊頭(顯示 A 製作、票連結賣 B)。三條規則:

1. presenter 滲入:id 含 -presents-/-presented-by- 的紀錄(TM event「XX presents YY」
   型,attraction=呈現方非製作)tour_name 必須為空。
2. 跨 attraction 撞名:同一「特定製作名」(非 (Touring)/(Non-Equity) 泛名)不得橫跨
   多個 TM attraction id —— 同名跨 attraction = 借名污染的指紋。
3. 純團名:tour_name 不得等於已知純團名(宝塚歌劇 等)。

違規列明細並 exit 1(CI 以 ::warning 呈現,與其他 audit 一致)。
"""
import json
import re
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
DATA = Path(__file__).resolve().parent.parent / "data"

PURE_COMPANY = {"宝塚歌劇"}
GENERIC_RE = re.compile(r"\((touring|non-equity)\)$", re.I)
_STOP = {"the", "a", "an", "of", "and", "le", "les", "la", "de", "musical", "on", "in"}


def _tokens(t):
    t = unicodedata.normalize("NFKD", t or "").encode("ascii", "ignore").decode()
    return set(re.findall(r"[a-z0-9]+", t.lower())) - _STOP


def art_id(s):
    m = re.search(r"/artist/(\d+)", s.get("attraction_url") or s.get("ticket_url") or "")
    return m.group(1) if m else None


def main():
    shows = json.loads((DATA / "shows.json").read_text(encoding="utf-8"))["shows"]
    bad = []

    for s in shows:
        sid, tn = s.get("id") or "", s.get("tour_name")
        # 場地冠名(venue 名自含 presented by,如 Roxian Theatre Presented By Citizens)排除
        venue_pb = "presented by" in (s.get("venue") or "").lower()
        # presents 型 id 的 tour_name 若與劇名有 token 重疊=同 attraction 借回的製作名
        # (Broadway In Boise presents Mrs. Doubtfire → 'Mrs. Doubtfire (Touring)'),可信;
        # 零重疊(團名/系列名)才是滲入。
        if (tn and ("-presents-" in sid or "-presented-by-" in sid) and not venue_pb
                and not (_tokens(s.get("title")) & _tokens(tn))):
            bad.append(f"presenter 滲入: {s.get('title')!r} tour_name={tn!r} @ {s.get('venue')} ({sid})")
        if tn and tn in PURE_COMPANY:
            bad.append(f"純團名: {s.get('title')!r} tour_name={tn!r} @ {s.get('venue')} ({sid})")

    by_name = defaultdict(set)
    for s in shows:
        tn = s.get("tour_name")
        if s.get("type") == "tour" and tn and not GENERIC_RE.search(tn):
            aid = art_id(s)
            if aid:
                by_name[(s.get("group"), tn)].add(aid)
    for (g, tn), ids in sorted(by_name.items()):
        if len(ids) > 1:
            bad.append(f"跨 attraction 撞名: group={g} tour_name={tn!r} attractions={sorted(ids)}")

    if bad:
        print(f"tour_name 稽核 FAIL:{len(bad)} 筆違規")
        for b in bad:
            print("  " + b)
        sys.exit(1)
    print("tour_name 稽核 PASS(presenter 滲入 0/純團名 0/跨 attraction 撞名 0)")


if __name__ == "__main__":
    main()
