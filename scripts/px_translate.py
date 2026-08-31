# -*- coding: utf-8 -*-
"""繁中 → 簡中「純翻譯」模式(不重新生成劇情)。

用途:某些冷門劇 Perplexity 生成的簡中版劇情整篇錯,但繁中版已逐部查證正確。
此時不該再賭一次生成,而是把**已查證正確的繁中版**交給 Perplexity 做在地化翻譯:
只轉語言與用語(中國大陸通用譯名/用語),**不得增刪或改寫任何情節與人物**。

驗收(不合格就重試,最多 MAX_TRY 次):
  1) 段落數必須與原文完全一致 —— 防漏段
  2) 字數比 0.80~1.25 —— 防摘要化或灌水
  3) 不得殘留繁體字(以常見繁簡對照字抽測)
  4) 不得出現「以下」「翻译如下」這類說明性開場

用法: python scripts/px_translate.py <input.json> <out.json>
input.json = [{"show": <原 show key>, "src": <繁中原文>}, ...]
"""
import sys, io, re, json, time, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from playwright.sync_api import sync_playwright

INP, OUT = sys.argv[1], sys.argv[2]
MAX_TRY = 6
END_OK = "。！？…」』）.!?\""
UI = {"回答","連結","圖片","分享","搜尋網路","來源","相關","匯出","重新生成","複製","Copy","Sources","Answer",
      "編輯","詢問","詢問後續問題","步驟","任務","Computer","下載","重寫","報告","Related","Share","Export","Rewrite"}
TS = re.compile(r"^(凌晨|早上|上午|中午|下午|晚上|傍晚|深夜)?\s*\d{1,2}[:：]\d{2}$")
PROGRESS = re.compile(r"^(查找|搜尋|搜索|查閱|查詢|正在|讀取|分析|生成|確認|翻查|整理|彙整|翻譯|翻译|Searching|Reading|Analyzing|Translating)")
# 抽測用的繁體字(這些字在簡體文本中不該出現)
TRAD = "為與這麼個們來對時後說產動務開關實現處點麼經濟會體區華書東馬車門長風飛" \
       "陣陳際隨階雙難靜韓題顯驗體驚讓認識語調議護讀變讓豐醫獸禮權歸歲歷"

PREFACE = re.compile(r"^(以下|下面|这是|這是|翻译|翻譯|译文|譯文|好的|当然|當然|Here|Sure|Below)")

def clean(text):
    lines = text.split("\n")
    keep = []
    for ln in lines:
        s = ln.strip()
        if not s:
            keep.append(ln); continue
        if s in UI: continue
        if TS.match(s): continue
        if re.fullmatch(r"\+\d+", s): continue
        if re.fullmatch(r"[a-z][a-z0-9\-]{1,}", s): continue
        if re.fullmatch(r"[a-z0-9.\-]+\.[a-z]{2,}", s, re.I): continue
        if PROGRESS.match(s) and len(s) < 40: continue
        if PREFACE.match(s) and len(s) < 60 and ("：" in s or ":" in s or len(s) < 24): continue
        keep.append(ln)
    paras = [p.strip() for p in re.split(r"\n\s*\n", "\n".join(keep).strip()) if p.strip()]
    while paras and paras[-1] and paras[-1][-1] not in END_OK:
        paras.pop()
    return "\n\n".join(paras).strip()

def paras_of(t):
    return [p for p in re.split(r"\n\s*\n", t.strip()) if p.strip()]

def trad_left(t):
    return sorted(set(c for c in t if c in TRAD))

def verdict(src, got):
    """回傳 (是否合格, 問題清單)"""
    bad = []
    ps, pg = len(paras_of(src)), len(paras_of(got))
    if pg != ps: bad.append("段落數 %d≠%d" % (pg, ps))
    if not got: bad.append("空白")
    else:
        ratio = len(got) / max(1, len(src))
        if not (0.80 <= ratio <= 1.25): bad.append("字數比 %.2f" % ratio)
    left = trad_left(got)
    if left: bad.append("繁體殘留 " + "".join(left[:8]))
    return (not bad), bad

def build_q(src):
    return (
        "请把下面这段繁体中文的音乐剧剧情简介翻译成简体中文，"
        "并改用中国大陆通用的译名与用语（人名、地名按大陆惯用译法；用词也改成大陆习惯说法）。\n"
        "严格要求：\n"
        "1. 只做语言与用语的转换，**绝对不要增加、删减或改写任何情节、人物、因果与结论**；\n"
        "2. 段落数必须与原文完全相同，逐段对应翻译；\n"
        "3. 不要加任何标题、说明、前言或注解，直接输出翻译后的正文。\n\n"
        "原文：\n" + src
    )

def wait_answer(p):
    prev, stable = None, 0
    for _ in range(40):
        p.wait_for_timeout(2000)
        try:
            body = p.inner_text("body")
            if "無法啟動工作階段" in body or "无法启动" in body or "Failed to start" in body:
                return ""
        except Exception:
            pass
        el = p.query_selector(".prose")
        cur = (el.inner_text().strip() if el else "")
        if len(cur) > 150 and cur == prev:
            stable += 1
            if stable >= 2: return cur
        else:
            stable = 0
        prev = cur
    return prev or ""

def get_box(p):
    for _ in range(20):
        b = p.query_selector("div[contenteditable='true']") or p.query_selector("textarea")
        if b: return b
        p.wait_for_timeout(1000)
    return None

def ask_once(ctx, Q):
    p = ctx.new_page()
    p.goto("https://www.perplexity.ai/", wait_until="domcontentloaded", timeout=60000)
    p.wait_for_timeout(2500)
    box = get_box(p)
    if not box:
        p.close(); return ""
    box.click()
    # ⚠ 不能直接 type 整段:contenteditable 裡的換行會被當成「送出」,
    # 結果只送出第一行指令、原文根本沒貼進去(Perplexity 會回「请把原文贴出来」)。
    # 逐行輸入,行間用 Shift+Enter 換行,最後才按 Enter 送出。
    lines = Q.split(chr(10))
    for i, ln in enumerate(lines):
        if i:
            p.keyboard.press("Shift+Enter")
        if ln:
            p.keyboard.type(ln, delay=2)
    p.wait_for_timeout(400)
    p.keyboard.press("Enter")
    raw = wait_answer(p); p.close()
    return clean(raw)

items = json.load(open(INP, encoding="utf-8"))
results = []
with sync_playwright() as pw:
    b = pw.chromium.connect_over_cdp("http://127.0.0.1:9223"); ctx = b.contexts[0]
    for i, it in enumerate(items):
        src = it["src"]; Q = build_q(src)
        best, best_bad = "", ["未取得"]
        for t in range(MAX_TRY):
            got = ask_once(ctx, Q)
            ok, bad = verdict(src, got)
            print("[%d/%d] #%d len=%d 段=%d %s" %
                  (i + 1, len(items), t + 1, len(got), len(paras_of(got)),
                   "OK" if ok else "／".join(bad)), flush=True)
            if ok:
                best, best_bad = got, []
                break
            if len(got) > len(best):
                best, best_bad = got, bad
            time.sleep(3 if got else 8)
        results.append({"show": it["show"], "synopsis": best,
                        "size": len(best), "paras": len(paras_of(best)),
                        "src_paras": len(paras_of(src)), "issues": best_bad})
        json.dump(results, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print("    -> %s" % ("合格" if not best_bad else "仍有問題: " + "／".join(best_bad)), flush=True)
print("DONE", flush=True)
