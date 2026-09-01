# -*- coding: utf-8 -*-
"""西葡 68 組「是不是音樂劇」查證帳本 —— 每一組的查證軌跡都要留下,供使用者 review。
用法: python scratchpad/eses/ledger.py add <group> <verdict> <json-payload-file>
      python scratchpad/eses/ledger.py report
verdict: musical | not_musical | uncertain
"""
import io, os, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
P = 'scratchpad/eses/ledger.json'

def load():
    if os.path.exists(P):
        return json.load(io.open(P, encoding='utf-8'))
    return {'_note': '西葡 68 組是否為音樂劇的逐組查證帳本。'
                     'sources=實際打開過的網址;evidence=逐字引文;verdict=判定;why=理由。'
                     '不確定者必須有 >=2 個獨立來源的交叉查證。', 'items': {}}

def save(d):
    json.dump(d, io.open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

def report():
    d = load(); it = d['items']
    import collections
    c = collections.Counter(v['verdict'] for v in it.values())
    print('已查 %d / 68 組  →  %s' % (len(it), dict(c)))
    for k in ('not_musical', 'uncertain', 'musical'):
        gs = [g for g, v in it.items() if v['verdict'] == k]
        if gs:
            print('\n【%s】%d 組' % (k, len(gs)))
            for g in sorted(gs):
                print('  %-44s %s' % (g[:44], it[g]['why'][:78]))

if __name__ == '__main__':
    if sys.argv[1] == 'report':
        report()
    elif sys.argv[1] == 'add':
        d = load()
        payload = json.load(io.open(sys.argv[2], encoding='utf-8'))
        for rec in payload:
            d['items'][rec['group']] = {k: rec[k] for k in ('verdict', 'why', 'sources', 'evidence', 'category') if k in rec}
        save(d)
        print('寫入 %d 筆,帳本現有 %d 組' % (len(payload), len(d['items'])))
