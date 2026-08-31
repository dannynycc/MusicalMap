# -*- coding: utf-8 -*-
"""跨語言一致性掃描:抓「整篇幻覺」型錯誤。

起因(2026-09-01):`Szeretve mind a vérpadig` 的簡中整篇是編的
(1870 年代 / 阿爾帕德 / 伊洛娜),而繁中與英文都正確。
前一輪只逐句比對繁中就結案,**這種錯完全看不到**。

偵測原理:同一部劇的繁中與簡中,講的是同一個故事,
把繁中經 OpenCC 轉成簡體後,兩者的**專有名詞用字**應大量重疊。
若重疊率極低 → 兩篇在講不同的故事 → 至少有一篇是幻覺。

另外兩個獨立訊號:
  * 年份集合:某個年份只出現在一種語言(常見於憑空編年代)
  * 長度比:一語明顯過短/過長

輸出是**待人工複查清單**,不是判決。
"""
import io, os, re, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

try:
    from opencc import OpenCC
    t2s = OpenCC('t2s').convert
except Exception:
    import subprocess
    def t2s(x):  # 沒有 python opencc 就用 node 的 opencc-js
        raise RuntimeError('need opencc')

LIB = 'data/synopses_library'
def load(name):
    d = json.load(io.open(LIB + '/' + name, encoding='utf-8'))
    return d.get('syn', d)          # 庫檔外層是 {_note, syn:{...}}

en, zht, zhs = load('en.json'), load('zh-hant.json'), load('zh-hans.json')

def body(d, g, sub):
    v = d.get(g)
    if isinstance(v, dict): v = v.get(sub)
    return v if isinstance(v, str) else ''

CJK = re.compile(r'[一-鿿]')
def cjk_bigrams(s):
    """只取中文字的 bigram —— 專有名詞(人名/地名)幾乎都是連續中文"""
    runs = re.findall(r'[一-鿿]{2,}', s)
    out = set()
    for r in runs:
        for i in range(len(r) - 1):
            out.add(r[i:i+2])
    return out

def years(s):
    return set(re.findall(r'(1[0-9]{3}|20[0-4][0-9])', s))

rows = []
for g in sorted(set(zht) | set(zhs)):
    a, b = body(zht, g, 'zh'), body(zhs, g, 'zh-hans')
    if not a or not b:
        continue
    A, B = cjk_bigrams(t2s(a)), cjk_bigrams(b)
    if not A or not B:
        continue
    jac = len(A & B) / float(len(A | B))
    ya, yb = years(a), years(b)
    ratio = len(b) / float(len(a)) if a else 0
    rows.append((jac, g, len(a), len(b), ratio, ya, yb))

rows.sort()
print('掃描 %d 組(繁中×簡中同時有內文者)' % len(rows))
print()
print('=== 用字重疊率最低的 25 組(越低越可疑) ===')
print('%-8s %-40s %6s %6s %6s  %s' % ('重疊率', 'group', '繁字數', '簡字數', '長度比', '年份差異'))
for jac, g, la, lb, ratio, ya, yb in rows[:25]:
    diff = ''
    if ya ^ yb:
        diff = '繁獨有%s 簡獨有%s' % (sorted(ya - yb) or '-', sorted(yb - ya) or '-')
    print('%7.3f  %-40s %6d %6d %6.2f  %s' % (jac, g[:40], la, lb, ratio, diff))

# 年份只出現在單一語言(獨立訊號)
print()
print('=== 年份只出現在其中一種語言的組(獨立訊號) ===')
n = 0
for jac, g, la, lb, ratio, ya, yb in rows:
    if ya ^ yb:
        n += 1
        if n <= 20:
            print('  %-40s 重疊率%.3f  繁:%s 簡:%s' % (g[:40], jac, sorted(ya) or '-', sorted(yb) or '-'))
print('  ...合計 %d 組' % n)

json.dump([{'group': g, 'jaccard': round(j, 4), 'len_zht': la, 'len_zhs': lb,
            'ratio': round(r, 3), 'years_zht': sorted(ya), 'years_zhs': sorted(yb)}
           for j, g, la, lb, r, ya, yb in rows],
          io.open('scratchpad/euro2/xlang_scan.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('\n完整結果 -> scratchpad/euro2/xlang_scan.json')
