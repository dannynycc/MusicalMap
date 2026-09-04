# -*- coding: utf-8 -*-
"""確定性清理:把 pipeline 抓到的原始 json 清成最終簡介。
用法: python polish.py <raw.json> <out_basename>
產出: <out_basename>.json / <out_basename>.md 於 data/synopses_draft/,並印真實字數。
"""
import json, io, re, sys, os

END_OK = "。！？…」』）.!?"
SRC = {"wikipedia", "britannica", "mtishows", "concordtheatricals", "broadwayinbound",
       "imdb", "playbill", "musico", "npac", "broadwaymusicalhome"}
PROGRESS = re.compile(r"^(查找|搜尋|搜索|查閱|查詢|正在|讀取|分析|生成|確認|翻查|整理|彙整)")
META = ("臺灣演出介紹", "台灣演出介紹", "所述版本", "版本一致", "資料來源", "官方資料",
        "以上內容", "以下內容", "如需")
# Perplexity 介面標籤(常以獨立行出現在答案前後):整行等於這些就刪
UI_LINES = {"回答", "連結", "圖片", "分享", "搜尋網路", "來源", "相關", "匯出", "重新生成",
            "複製", "Copy", "Sources", "Answer", "編輯", "詢問", "詢問後續問題",
            "步驟", "任務", "Computer", "下載", "重寫", "報告", "匯出至 PDF", "轉換為 PDF"}


_TW_MAP = None
def _load_tw_map():
    global _TW_MAP
    if _TW_MAP is None:
        try:
            _TW_MAP = json.load(open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "synopses_tw_terms.json"),
                                     encoding="utf-8")).get("map", {})
        except Exception as ex:
            # 🚨 原本這裡是靜默吞掉的。表載不進來時 normalize_tw() 會變成【什麼都不做】,
            #    而呼叫端只看到「回傳了文字」——中港譯名就這樣一路寫進庫裡而沒有任何跡象。
            sys.stderr.write("::warning::台灣定譯表載入失敗(%s),normalize_tw 這輪不會做任何替換%s"
                             % (ex, chr(10)))
            _TW_MAP = {}
    return _TW_MAP


def normalize_tw(text):
    """套用台灣定譯對照表:中國/香港譯名 → 台灣慣用。回傳 (新文字, [(from,to,次數)...])。"""
    m = _load_tw_map()
    changes = []
    for src, dst in m.items():
        if src == dst:
            continue
        n = text.count(src)
        if n:
            text = text.replace(src, dst)
            changes.append((src, dst, n))
    return text, changes


def polish(ans):
    lines = ans.split("\n")
    # 去開頭:空行 / 時間戳 / 進度狀態行 / UI 標籤(回答/連結/圖片/分享…分行出現)
    while lines:
        s = lines[0].strip()
        if (not s or re.fullmatch(r"[上中下]午\s*\d{1,2}[:：]\d{2}", s)
                or PROGRESS.match(s) or s in UI_LINES):
            lines.pop(0)
        else:
            break
    # 逐行過濾:UI 標籤 / 純來源名 / 網域 / meta 廢話 / 進度行(任何位置)
    keep = []
    for ln in lines:
        s = ln.strip()
        if not s:
            keep.append(ln)
            continue
        if s in UI_LINES:
            continue
        if s.lower() in SRC:
            continue
        if re.fullmatch(r"[a-z0-9.\-]+\.[a-z]{2,}", s, re.I):
            continue
        if PROGRESS.match(s) and len(s) < 30:
            continue
        if any(k in s for k in META):
            continue
        keep.append(ln)
    text = "\n".join(keep).strip()
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    # 尾段非句末標點(=建議追問標題)一律砍
    while paras and paras[-1][-1] not in END_OK:
        paras.pop()
    out = "\n\n".join(paras).strip()
    out, _ = normalize_tw(out)   # 台灣定譯正規化(中港譯名→台灣慣用),自動套用
    return out


def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    raw = json.load(open(sys.argv[1], encoding="utf-8"))
    base = sys.argv[2]
    outdir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "synopses_draft")
    os.makedirs(outdir, exist_ok=True)
    clean = []
    for r in raw:
        p = polish(r["answer"])
        n = len(p)
        band = "OK" if 400 <= n <= 450 else ("短" if n < 400 else "長")
        clean.append({"show": r["show"], "synopsis": p, "len": n, "band": band})
    json.dump(clean, open(os.path.join(outdir, base + ".json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    md = [f"# 音樂劇簡介草稿 — {base}\n",
          "> Perplexity 原文，已清介面雜訊。台灣譯名／不提小說。目標 400–450 字。\n"]
    for c in clean:
        md.append(f"\n## {c['show']}（{c['len']}字・{c['band']}）\n")
        md.append(c["synopsis"] + "\n")
    open(os.path.join(outdir, base + ".md"), "w", encoding="utf-8", newline="\n").write("\n".join(md))
    print("字數統計:")
    for c in clean:
        print(f"  {c['band']:2s} {c['len']:4d}  {c['show']}")
    print(f"\n存於 {outdir}\\{base}.md")


if __name__ == "__main__":
    main()
