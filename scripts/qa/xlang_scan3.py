# -*- coding: utf-8 -*-
"""跨語言一致性掃描 v3。

v2 失敗紀錄(必讀,別再走一次):
  v2 用「重複出現的 3 字序列」當專名代理,對已知陽性 0.000 / 修正後 1.000,看似完美。
  但全庫有大量 0.000 —— 因為**繁簡各自獨立生成時,音譯人名本來就不同**
  (a christmas carol:繁「史古基」vs 簡「斯克鲁奇」)。
  該指標其實在測「這篇是不是翻譯來的」,不是測幻覺。**作廢。**

v3 改用**不受音譯影響**的訊號:
  (1) bigram Jaccard —— 但要拿已知陽性去比對全庫分布才知道閾值在哪
  (2) 年份集合差異 —— 年份不受音譯影響,是硬錨點
"""
import io, re, sys, json, statistics as st
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from opencc import OpenCC
t2s = OpenCC('t2s').convert

def bigrams(s):
    out = set()
    for run in re.findall(r'[一-鿿]{2,}', s):
        for i in range(len(run) - 1):
            out.add(run[i:i+2])
    return out

def jac(a, b):
    A, B = bigrams(t2s(a)), bigrams(b)
    return len(A & B) / float(len(A | B)) if A and B else None

def load(n):
    d = json.load(io.open('data/synopses_library/' + n, encoding='utf-8'))
    return d.get('syn', d)

zht, zhs = load('zh-hant.json'), load('zh-hans.json')
G = 'vizeli szeretve mind a verpadig'
ref = zht[G]['zh']
_fx = json.load(io.open('scripts/qa/fixtures/known_positive.json', encoding='utf-8'))
bad = _fx['hallucinated_zhs']

rows = []
for g in sorted(set(zht) & set(zhs)):
    a = zht[g].get('zh') if isinstance(zht[g], dict) else None
    b = zhs[g].get('zh-hans') if isinstance(zhs[g], dict) else None
    if not a or not b: continue
    j = jac(a, b)
    if j is not None: rows.append((j, g))
rows.sort()
vals = [r[0] for r in rows]
j_bad = jac(ref, bad)

print('【已知陽性】Szeretve 修正前(整篇幻覺) bigram Jaccard = %.4f' % j_bad)
print('【全庫 %d 組】最低 %.4f / 第1百分位 %.4f / 下四分位 %.4f / 中位 %.4f'
      % (len(rows), vals[0], vals[max(0, len(vals)//100)], vals[len(vals)//4], st.median(vals)))
below = [g for j, g in rows if j <= j_bad]
print('\n→ 全庫中分數 <= 已知陽性的組:%d 個' % len(below))
if len(below) <= 30:
    for j, g in rows:
        if j <= j_bad: print('   %.4f  %s' % (j, g))
verdict = '有區辨力' if j_bad < vals[max(0, len(vals)//100)] else '**無區辨力,不可用**'
print('\n判定:已知陽性 %.4f vs 全庫第1百分位 %.4f → %s' % (j_bad, vals[max(0, len(vals)//100)], verdict))
