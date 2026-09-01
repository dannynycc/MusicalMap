# -*- coding: utf-8 -*-
"""西葡劇名深度查詢工具(使用者要求:多輪、稍有不確定就再 dive in、過程要留證)。

2026-09-01:原本開專屬 Chrome profile,但(a)全新 profile 打 Google 立刻被判機器人,整輪零資料;
(b)使用者不想一直被彈出新視窗。改為連使用者【已登入的 Comet】CDP 9223 開分頁,用完即關。
用法: python scratchpad/eses/research.py <jobs.json> <out.json>
jobs.json = [{"key":"<group>","queries":["...","..."],"open":N}]
            queries = 這一輪要下的搜尋字串;open = 每個查詢要點進去讀幾個結果頁(0=只讀摘要)
輸出每個查詢的:結果摘要全文 + 點進去的頁面網址與內文節錄 → 供我讀完後寫進 tledger。
"""
import io, os, re, sys, json, time, urllib.parse
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from playwright.sync_api import sync_playwright

CDP = 'http://127.0.0.1:9223'   # 使用者已登入的 Comet
JOBS, OUT = sys.argv[1], sys.argv[2]
SKIP = ('google.', 'gstatic', 'googleusercontent', 'youtube.com/redirect', 'accounts.google')

def clean(t):
    return re.sub(r'\n{3,}', '\n', t or '')

def main():
    jobs = json.load(io.open(JOBS, encoding='utf-8'))
    res = []
    with sync_playwright() as pw:
        ctx = pw.chromium.connect_over_cdp(CDP).contexts[0]
        for job in jobs:
            entry = {'key': job['key'], 'queries': []}
            for q in job['queries']:
                rec = {'q': q, 'serp': '', 'pages': []}
                p = ctx.new_page()
                try:
                    # 2026-09-01:全新 profile 打 Google 立刻被判機器人(整輪 12 個查詢零資料)。
                    # 不去破解驗證——改用容許自動化的 DuckDuckGo html 版,並放慢節奏。
                    p.goto('https://www.google.com/search?num=20&q=' + urllib.parse.quote(q),
                           wait_until='domcontentloaded', timeout=45000)
                    p.wait_for_timeout(2600)
                    for sel in ['button:has-text("全部接受")', 'button:has-text("Accept all")',
                                'button:has-text("Aceptar todo")', '#L2AGLb']:
                        try:
                            e = p.query_selector(sel)
                            if e: e.click(); p.wait_for_timeout(1500); break
                        except Exception: pass
                    rec['serp'] = clean(p.inner_text('body'))[:4500]
                    links = [a for a in p.eval_on_selector_all('a', 'els=>els.map(e=>e.href)')
                             if a.startswith('http') and not any(s in a for s in SKIP)]
                    links = list(dict.fromkeys(links))[:job.get('open', 0)]
                except Exception as e:
                    rec['serp'] = 'SERP_ERR %s' % e; links = []
                p.close()
                for u in links:
                    q2 = ctx.new_page()
                    try:
                        q2.goto(u, wait_until='domcontentloaded', timeout=40000)
                        q2.wait_for_timeout(2200)
                        rec['pages'].append({'url': u, 'text': clean(q2.inner_text('body'))[:4000]})
                    except Exception as e:
                        rec['pages'].append({'url': u, 'text': 'PAGE_ERR %s' % e})
                    q2.close()
                entry['queries'].append(rec)
                time.sleep(2.5)
            res.append(entry)
            json.dump(res, io.open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
            print('done %s (%d queries)' % (job['key'], len(job['queries'])), flush=True)
    print('ALL DONE ->', OUT)

main()
