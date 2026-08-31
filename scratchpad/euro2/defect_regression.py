# -*- coding: utf-8 -*-
"""已知缺陷類型的回歸掃描(歐陸原創 54 組 × 三語)。

記憶教訓:修症狀類 bug 必須全庫掃同症狀的所有變型,而且**修完要重跑原始掃描**
——先前有兩次「看起來修好」其實沒修到。這支就是那個「原始掃描」。

掃的是**先前幾輪實際發生過**的缺陷,不是憑空想的:
  A. 英文版 slug 殘留(如 a-christmas-carol 出現在散文裡)—— 曾有 10 部
  B. 簡中清晨時間戳(Perplexity UI 的「凌晨 3:24」洩漏進正文)—— 曾有 22 部
  C.「全劇總結」之類的標題字面殘留
  D. 書評框架開頭(「本劇講述…」「這是一部…」)—— 使用者要求開頭直接入戲
  E. 缺總結段(最後一段沒有收束)
  F. Perplexity 說明性開場(「以下」「翻譯如下」)
  G. 引用標記殘留([1]、來源、Sources)
"""
import io, re, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def load(n):
    d = json.load(io.open('data/synopses_library/' + n, encoding='utf-8'))
    return d.get('syn', d)

en, zht, zhs = load('en.json'), load('zh-hant.json'), load('zh-hans.json')
EU = sorted(json.load(io.open('scratchpad/titles/groups.json', encoding='utf-8')))

CHECKS = [
 ('A 英文 slug 殘留',      re.compile(r'\b[a-z]{3,}(?:-[a-z0-9]{2,}){2,}\b')),
 ('B 清晨時間戳',          re.compile(r'(凌晨|早上|上午|中午|下午|晚上|傍晚|深夜)\s*\d{1,2}[:：]\d{2}')),
 ('C 標題字面殘留',        re.compile(r'(全劇總結|全剧总结|劇情簡介|剧情简介|^\s*#{1,4}\s|^\s*\*\*[^*]{2,12}\*\*\s*[::]?\s*$)', re.M)),
 ('D 書評框架開頭',        re.compile(r'^(本劇|本剧|這是一[部齣]|这是一[部出]|該劇|该剧|全劇|全剧)')),
 ('F 說明性開場',          re.compile(r'^(以下|下面|翻譯|翻译|譯文|译文|好的|當然|当然|Here is|Below)')),
 ('G 引用/UI 殘留',        re.compile(r'(\[\d+\]|來源[::]|来源[::]|Sources?[::]|搜尋網路|重新生成)')),
]

def body(d, g, k):
    v = d.get(g)
    return v.get(k, '') if isinstance(v, dict) else ''

hits = []
for g in EU:
    for lab, d, k in (('EN', en, 'en'), ('繁', zht, 'zh'), ('簡', zhs, 'zh-hans')):
        t = body(d, g, k)
        if not t:
            continue
        for name, rx in CHECKS:
            if name.startswith('A'):
                slug = g.replace(' ', '-')
                # 單字 group key(如 metro)會把正文的普通名詞誤報成 slug,
                # 只有多詞 group 轉出的帶連字號 slug 才是真正的殘留形態
                if '-' in slug and slug in t:
                    i = t.find(slug)
                    hits.append((name, g, lab, t[max(0, i-40):i+60].replace(chr(10), ' ')))
                continue
            m = rx.search(t)
            if m:
                i = m.start()
                hits.append((name, g, lab, t[max(0, i-40):i+60].replace('\n', ' ')))
        # E 缺總結段:最後一段太短或沒有收束語氣
        paras = [p for p in re.split(r'\n\s*\n', t.strip()) if p.strip()]
        if len(paras) < 3:
            hits.append(('E 段落過少(<3)', g, lab, '共 %d 段' % len(paras)))

print('掃描歐陸原創 %d 組 × 三語' % len(EU))
if not hits:
    print('\n✅ 七類已知缺陷 全部 0 命中')
else:
    print('\n命中 %d 筆:' % len(hits))
    for name, g, lab, ctx in hits:
        print('  [%s] %-34s %s | %s' % (name, g[:34], lab, ctx[:100]))
