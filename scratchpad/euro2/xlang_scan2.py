# -*- coding: utf-8 -*-
"""跨語言一致性掃描 v2 —— 只比對「核心專名」。

v1 用 bigram Jaccard,全庫都落在 0.07~0.10,沒有區辨力:
兩篇獨立生成的中文即使講同一故事,普通用詞也差很多,把專名訊號稀釋掉了。

v2 改用「**在同一篇裡重複出現 >=2 次的 3 字中文序列**」當專名代理:
人名、地名、劇中核心概念才會在一篇 400 字的簡介裡出現兩次以上。
同一部劇的繁簡兩版,核心專名(音譯字)應大量重疊;
若重疊為 0 → 兩篇在講不同的故事。

⚠ 這是**待人工複查清單**,不是判決。先用已知陽性(Szeretve 修正前的幻覺版)驗證區辨力。
"""
import io, re, sys, json, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from opencc import OpenCC
t2s = OpenCC('t2s').convert

def core_names(s, n=3, minc=2):
    s = re.sub(r'[^一-鿿]', ' ', s)
    c = collections.Counter()
    for run in s.split():
        for i in range(len(run) - n + 1):
            c[run[i:i+n]] += 1
    return set(k for k, v in c.items() if v >= minc)

def score(zht_text, zhs_text):
    A, B = core_names(t2s(zht_text)), core_names(zhs_text)
    if not A or not B:
        return None, len(A), len(B)
    return len(A & B) / float(min(len(A), len(B))), len(A), len(B)

def load(name):
    d = json.load(io.open('data/synopses_library/' + name, encoding='utf-8'))
    return d.get('syn', d)

zht, zhs = load('zh-hant.json'), load('zh-hans.json')

# --- 步驟 1:先驗證檢測器對已知陽性有效(否則就是球員兼裁判) ---
GRP = 'vizeli szeretve mind a verpadig'
cur = zhs[GRP]['zh-hans']
bad = [x for x in json.load(io.open('scratchpad/euro2/gen/out_zhs.before_fix.json', encoding='utf-8'))
       if x['show'].startswith('Szeretve')][0]['synopsis']
ref = zht[GRP]['zh']
s_bad, a1, b1 = score(ref, bad)
s_ok,  a2, b2 = score(ref, cur)
print('【檢測器驗證】Szeretve mind a vérpadig')
print('  修正前(已知整篇幻覺):重疊 %.3f  (繁核心名%d / 簡核心名%d)' % (s_bad, a1, b1))
print('  修正後(繁中純翻譯)  :重疊 %.3f  (繁核心名%d / 簡核心名%d)' % (s_ok,  a2, b2))
print('  → 區辨力 %s' % ('OK,可用於全庫掃描' if s_ok - s_bad > 0.3 else '不足,不可用'))
print()

# --- 步驟 2:全庫掃描 ---
rows = []
for g in sorted(set(zht) & set(zhs)):
    a = zht[g].get('zh') if isinstance(zht[g], dict) else None
    b = zhs[g].get('zh-hans') if isinstance(zhs[g], dict) else None
    if not a or not b:
        continue
    sc, na, nb = score(a, b)
    if sc is None:
        continue
    rows.append((sc, g, na, nb, len(a), len(b)))
rows.sort()
print('【全庫掃描】%d 組' % len(rows))
import statistics as st
vals = [r[0] for r in rows]
print('  重疊分布:中位數 %.3f  下四分位 %.3f  最低 %.3f' %
      (st.median(vals), vals[len(vals)//4], vals[0]))
print()
print('=== 重疊最低的 20 組(需人工複查) ===')
print('%-7s %-42s %5s %5s' % ('重疊', 'group', '繁名', '簡名'))
for sc, g, na, nb, la, lb in rows[:20]:
    print('%6.3f  %-42s %5d %5d' % (sc, g[:42], na, nb))
json.dump([{'group': g, 'overlap': round(s, 4), 'names_zht': na, 'names_zhs': nb}
           for s, g, na, nb, la, lb in rows],
          io.open('scratchpad/euro2/xlang_scan2.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
