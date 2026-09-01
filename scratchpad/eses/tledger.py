# -*- coding: utf-8 -*-
"""西葡 59 組「中文劇名」查證帳本 —— 使用者要 review 我的思考與執行過程,所以每組都要留下:
   rounds  : 逐輪查詢做了什麼(查詢字串 / 開了哪些頁 / 看到什麼 / 為何還不夠要再查)
   sources : 實際打開過的網址
   evidence: 逐字引文(原文,不要我的轉述)
   verdict : translate(翻) | keep(保留原文) | pending(還在查)
   tw / cn : 繁體 / 簡體 譯名
   why     : 判定理由
   confidence: high | medium | low  —— low 一定要寫清楚為什麼還是低

用法:
  python scratchpad/eses/tledger.py add <payload.json>   # payload = [{group:..., ...}, ...] 以 group 覆蓋
  python scratchpad/eses/tledger.py round <group> <round.json>  # 只追加一輪查詢紀錄
  python scratchpad/eses/tledger.py report
"""
import io, os, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
P = 'scratchpad/eses/titles_ledger.json'

def load():
    if os.path.exists(P):
        return json.load(io.open(P, encoding='utf-8'))
    return {'_note': '西葡 59 組中文劇名的逐組查證帳本。使用者(2026-09-01)要求:必須多輪深度查詢、'
                     '稍有不確定就要再 dive in 查更多網頁交叉比對,且思考與執行過程都要寫進來供 review。'
                     '規則沿用歐陸:普通名詞/片語→翻(需詞義依據);純專有名詞/虛構人名→保留原文(音譯不發明)。'
                     '⚠ 人名劇「加副標」的例外只適用歐陸,西葡不適用。',
            'items': {}}

def save(d):
    json.dump(d, io.open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

def main():
    cmd = sys.argv[1]
    d = load()
    if cmd == 'add':
        for rec in json.load(io.open(sys.argv[2], encoding='utf-8')):
            g = rec['group']
            cur = d['items'].get(g, {})
            cur.setdefault('rounds', [])
            cur['rounds'] = cur['rounds'] + rec.pop('rounds', [])
            cur.update(rec)
            d['items'][g] = cur
        save(d); print('寫入完成,帳本現有 %d 組' % len(d['items']))
    elif cmd == 'round':
        g = sys.argv[2]
        cur = d['items'].setdefault(g, {'verdict': 'pending', 'rounds': []})
        cur['rounds'] += json.load(io.open(sys.argv[3], encoding='utf-8'))
        save(d); print('%s 現有 %d 輪紀錄' % (g, len(cur['rounds'])))
    else:
        it = d['items']
        import collections
        c = collections.Counter(v.get('verdict', '?') for v in it.values())
        print('已處理 %d / 59 組 → %s' % (len(it), dict(c)))
        conf = collections.Counter(v.get('confidence', '?') for v in it.values())
        print('信心分布: %s' % dict(conf))
        for g, v in sorted(it.items()):
            print('  %-42s %-9s 繁=%-14s 輪數=%d %s'
                  % (g[:42], v.get('verdict', '?'), str(v.get('tw') or '-')[:14],
                     len(v.get('rounds', [])), '⚠低信心' if v.get('confidence') == 'low' else ''))

main()
