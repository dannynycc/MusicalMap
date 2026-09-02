# -*- coding: utf-8 -*-
"""西葡 58 組「三語劇情簡介」查核帳本 —— 使用者要在過程中檢視證據,所以每組都要留下:
   rounds       : 逐輪查核做了什麼(目的 / 查詢字串 / 開啟頁面 / 看到什麼逐字原文 / 判斷)
   sources      : 實際打開過的網址(優先序:製作方官網 > 劇院官方頁 > 劇評/媒體 > 售票平台)
   official_plot: 官方/權威來源的劇情逐字原文(查核的比對基準)
   checks       : 三維度逐項比對結果 —— plot(劇情正確性) / facts(事實) / semantics(語意)
                  每項寫「生成說了什麼 → 來源怎麼說 → 判定(✓吻合 / ✗捏造 / △未證實 / ⚠遺漏)」
   fixes        : 改了什麼、為什麼改
   confidence   : high | medium | low(low 要寫清楚為何仍低)
   verify_scope : 查核到什麼程度(多源交叉 / 單一官方源 / 僅內部一致性)——不可謊報

用法:
  python scratchpad/eses/sledger.py add <payload.json>   # payload=[{group:..., ...}] 以 group 覆蓋
  python scratchpad/eses/sledger.py report
"""
import io, os, sys, json, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
P = 'scratchpad/eses/synopsis_ledger.json'
TOTAL = 55   # 清單 64 組:urinetown 已有簡介、8 組已下檔退出目錄(見 scratchpad/eses/scope.json),實際需做 55 組

def load():
    if os.path.exists(P):
        return json.load(io.open(P, encoding='utf-8'))
    return {'_note': '西葡 58 組三語劇情簡介的逐組查核帳本(2026-09-02)。'
                     '使用者要求:多個 source、深度查證、交叉比對,不是找兩個網頁交差;'
                     '過程要留證據供檢視。流程沿用既有規則:Perplexity 生成=主體(語感),'
                     '我=查核正確性(劇情/事實/語意三維度缺一不可)。'
                     '⚠ 實測結論(見 _pilot):Perplexity 對西葡這批劇【確實有真實知識】,'
                     '連極冷門的加泰語小劇 Un refugi al sol 都能吐出被官方頁逐字印證的細節,'
                     '故不改走「先餵原文」路線;但查核一步都不能省。',
            '_pilot': {}, 'items': {}}

def save(d):
    json.dump(d, io.open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'report'
    d = load()
    if cmd == 'add':
        for rec in json.load(io.open(sys.argv[2], encoding='utf-8')):
            if rec.get('_pilot'):
                d['_pilot'] = rec; continue
            g = rec['group']
            cur = d['items'].get(g, {})
            # ⚠ cur.update(rec) 會【整個換掉】同名欄位。2026-09-02 寫繁中紀錄時就是這樣把英文那輪的
            #    fixes 洗掉的(el ladron de arabia 只剩 1 筆)。所以累積型欄位一律走 *_add 走 append,
            #    payload 裡不要再直接給 fixes/sources/rounds 整包覆蓋。
            for key, addkey in (('rounds', 'rounds'), ('fixes', 'fixes_add'),
                                ('sources', 'sources_add')):
                add = rec.pop(addkey, [])
                if add:
                    cur[key] = (cur.get(key) or []) + add
            cur.update(rec)
            d['items'][g] = cur
        save(d); print('寫入完成,帳本現有 %d 組' % len(d['items']))
    else:
        it = d['items']
        c = collections.Counter(v.get('confidence', '?') for v in it.values())
        done = [g for g, v in it.items() if v.get('done')]
        print('已查核 %d / %d 組(已入庫 %d)  信心分布 %s'
              % (len(it), TOTAL, len(done), dict(c)))
        nf = sum(len(v.get('fixes') or []) for v in it.values())
        print('累計修正 %d 處' % nf)
        for g, v in sorted(it.items()):
            print('  %-42s %-7s 輪數=%d 修正=%d %s'
                  % (g[:42], v.get('confidence', '?'), len(v.get('rounds', [])),
                     len(v.get('fixes') or []), '✓入庫' if v.get('done') else ''))

main()
