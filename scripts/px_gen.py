# -*- coding: utf-8 -*-
"""統一三語簡介生成:抓取→到達字數+總結→清理→(zh-hant 套 normalize_tw)→寫檔。
不在此刪歷史(交給 px_del.py 用正確 aria-label『工作階段動作』收尾)。
用法: python px_gen.py <en|zh-hant|zh-hans> <out.json> @<list.json>
list.json = 英文劇名陣列(prompt 前綴);各語言靠 prompt 指示產生對應譯名。
"""
import sys, io, re, json, time, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # 同目錄找 polish.py
from playwright.sync_api import sync_playwright
LANG, OUT, LIST = sys.argv[1], sys.argv[2], sys.argv[3]

if LANG == "en":
    TAIL = (" — the musical. Write a plot synopsis of about 280 words as a single flowing article in English, "
            "using character and place names as used in English-language productions. "
            "IMPORTANT: end with a SEPARATE final paragraph of two to three sentences summarising the whole "
            "show's themes. "
            "Describe only the plot; do not mention the original source material, your sources, or version notes.")
    LO, HI, CENTER = 220, 340, 280
    size = lambda t: len(t.split())
elif LANG == "zh-hans":
    TAIL = ("音乐剧 用约380字介绍剧情（写成一篇文章，简体中文，使用中国大陆通用的译名与用语）。"
            "全文连同结尾总结务必控制在400到450字之间，绝对不要超过450字，宁可精简剧情细节。"
            "务必在文章最后独立分一段写全剧总结，长度两到三句。"
            "只描述剧情本身，不要提到原著小说，也不要说明资料来源或版本比对。")
    LO, HI, CENTER = 400, 450, 425
    size = lambda t: len(t)
else:  # zh-hant
    TAIL = ("音樂劇 用約420字介紹劇情（寫成一篇文章，台灣繁體中文，使用台灣慣用的譯名與用語），字數控制在400到460字之間。"
            "務必在文章最後獨立分一段寫全劇總結，長度兩到三句。"
            "只描述劇情本身，不要提到原著小說，也不要說明資料來源或版本比對。")
    LO, HI, CENTER = 400, 450, 425
    size = lambda t: len(t)

MAX_TRY = 7
END_OK = "。！？…」』）.!?\""
UI = {"回答","連結","圖片","分享","搜尋網路","來源","相關","匯出","重新生成","複製","Copy","Sources","Answer",
      "編輯","詢問","詢問後續問題","步驟","任務","Computer","下載","重寫","報告","Related","Share","Export","Rewrite"}
TS = re.compile(r"^(凌晨|早上|上午|中午|下午|晚上|傍晚|深夜)?\s*\d{1,2}[:：]\d{2}$")
PROGRESS = re.compile(r"^(查找|搜尋|搜索|查閱|查詢|正在|讀取|分析|生成|確認|翻查|整理|彙整|Searching|Reading|Analyzing)")

def has_summary(text):
    paras = [p.strip() for p in text.split("\n\n") if p.strip()]
    if len(paras) < 2: return False
    last = paras[-1]
    plot_avg = sum(len(x) for x in paras[:-1]) / max(1, len(paras) - 1)
    if LANG == "en":
        w = len(last.split())
        cues = ("ultimately","at its heart","at heart","the musical","the show","a celebration","celebrat",
                "explores","is a story","a story of","in the end","more than","a testament","reminds",
                "becomes a","captures","affirms","is about","speaks to","a tale of","a portrait")
        plot_w = sum(len(x.split()) for x in paras[:-1]) / max(1, len(paras)-1)
        return 10 <= w <= 90 and any(c in last.lower() for c in cues)
    if last[:2] in ("全劇","全剧","本劇","本剧","整齣","整出","這齣","这出","全戲","全戏","該劇","该剧"): return True
    th = ("描寫","描写","呈現","呈现","探討","探讨","叩問","叩问","揭示","象徵","象征","刻劃","刻画","訴說","诉说","道出","反映",
          "歌頌","歌颂","是一齣","是一出","是一部關於","是一場","是一场","提醒","啟示","启示","昇華","升华","交織","交织",
          "終究","终究","對照","对照","證明","证明","明白","懂得","值得","學會","学会","不再","不必","真正的","真正值得",
          "所謂","所谓","本質","本质","代價","代价","意義","意义","主題","主题","不只是","不僅是","不仅是")
    return 15 <= len(last) <= 200 and any(k in last for k in th)

def clean(text, q):
    lines = text.split("\n")
    qn = re.sub(r"\s+","",q)
    while lines:
        s=lines[0].strip()
        if (not s or TS.match(s) or PROGRESS.match(s) or s in UI): lines.pop(0)
        else: break
    keep=[]
    for ln in lines:
        s=ln.strip()
        if not s: keep.append(ln); continue
        if s in UI: continue
        if re.fullmatch(r"\+\d+", s): continue                       # 售票來源殘留 +1/+2
        if re.fullmatch(r"(opentix|udn|tixfun|kktix|klook|拓元)", s, re.I): continue
        if re.match(r"^(Searching|Reading|Analyzing|Looking|Gathering|Checking)", s): continue  # 英文進度行
        if TS.match(s): continue
        if re.sub(r"\s+","",s)==qn: continue
        if re.fullmatch(r"(wikipedia|britannica|theatermania|stageagent|mtishows|playbill|broadwayworld|whatsonstage|concordtheatricals|londontheatre|masterworksbroadway|broadwaymusicalhome|theatregold|seatplan|ibdb|fandom|broadway|[a-z0-9.\-]+\.[a-z]{2,})",s,re.I): continue  # 來源名殘留(Perplexity 內文引註)
        if PROGRESS.match(s) and len(s)<40: continue
        keep.append(ln)
    paras=[p.strip() for p in re.split(r"\n\s*\n","\n".join(keep).strip()) if p.strip()]
    while paras and paras[-1] and paras[-1][-1] not in END_OK: paras.pop()
    out="\n\n".join(paras).strip()
    if LANG == "zh-hant":
        try:
            from polish import normalize_tw
            out,_=normalize_tw(out)
        except Exception: pass
    return out

def score(t):
    return (has_summary(t) and LO<=size(t)<=HI, has_summary(t), -abs(size(t)-CENTER))

def wait_answer(p):
    # Perplexity 答案本文在 .prose(乾淨、無 UI/回音/來源雜訊)。之前讀 main 會混入 UI 且時常抓不到答案。
    prev, stable = None, 0
    for _ in range(40):
        p.wait_for_timeout(2000)
        # 真錯誤:「無法啟動工作階段 / Failed to start」→ 立即放棄,快速重試
        try:
            body = p.inner_text("body")
            if "無法啟動工作階段" in body or "无法启动" in body or "Failed to start" in body:
                return ""
        except Exception:
            body = ""
        el = p.query_selector(".prose")
        cur = (el.inner_text().strip() if el else "")
        if len(cur) > 150 and cur == prev:
            stable += 1
            if stable >= 2:
                return cur
        else:
            stable = 0
        prev = cur
    return prev or ""

def get_box(p):
    for _ in range(20):   # 最多等 ~20s 讓輸入框出現(Comet 剛重啟時頁面較慢)
        b=p.query_selector("div[contenteditable='true']") or p.query_selector("textarea")
        if b: return b
        p.wait_for_timeout(1000)
    return None

def ask_once(ctx,Q):
    p=ctx.new_page()
    p.goto("https://www.perplexity.ai/",wait_until="domcontentloaded",timeout=60000)
    p.wait_for_timeout(2500)
    box=get_box(p)
    if not box:
        p.close(); return ""   # 拿不到輸入框→回空,交由重試(不讓整批崩潰)
    box.click(); p.keyboard.type(Q,delay=5); p.keyboard.press("Enter")
    raw=wait_answer(p); p.close()
    return clean(raw,Q)

SHOWS=json.load(open(LIST[1:],encoding="utf-8")) if LIST.startswith("@") else [LIST]
# 續跑:OUT 已有且該筆已達標(有總結+落在字數區間)就跳過,避免崩潰後重跑
results=[]; done={}
import os
if os.path.exists(OUT):
    try:
        for r in json.load(open(OUT,encoding="utf-8")):
            if r.get("summary") and (LANG=='en' and LO<=r.get('size',0)<=HI or LANG!='en' and 400<=r.get('size',0)<=460):
                done[r["show"]]=r
    except Exception: pass
with sync_playwright() as pw:
    b=pw.chromium.connect_over_cdp("http://127.0.0.1:9223"); ctx=b.contexts[0]
    for si,show in enumerate(SHOWS):
        if show in done:
            results.append(done[show]); json.dump(results,open(OUT,"w",encoding="utf-8"),ensure_ascii=False,indent=2)
            print(f"[{si+1}/{len(SHOWS)}] {show} 已達標,跳過",flush=True); continue
        Q=show+TAIL; attempts=[]; fails=0
        for t in range(MAX_TRY):
            a=ask_once(ctx,Q); attempts.append(a)
            print(f"[{si+1}/{len(SHOWS)}] {show} #{t+1} size={size(a)} sum={'Y' if has_summary(a) else 'N'}",flush=True)
            if LO<=size(a)<=HI and has_summary(a): break
            if len(a)==0:            # 啟動失敗/空 → 遞增退避,避免連打觸發更多失敗
                fails+=1; time.sleep(min(3+fails*3, 20))
            else:
                time.sleep(2)        # 有生成內容,短間隔
        best=max(attempts,key=score)
        results.append({"show":show,"synopsis":best,"size":size(best),"summary":has_summary(best)})
        json.dump(results,open(OUT,"w",encoding="utf-8"),ensure_ascii=False,indent=2)
        print(f"    -> best size={size(best)} sum={'Y' if has_summary(best) else 'N'}",flush=True)
        time.sleep(1)
print("DONE",flush=True)
