# -*- coding: utf-8 -*-
"""繁中→簡中翻譯稿的「用語有沒有真的換」檢查(px_translate 的配套驗收)。

使用者要求逐字:「拿繁中結果的去叫 perplexity 翻成簡體的語意(**並且使用中國用語**)」。
OpenCC 只轉字不轉詞 —— 若模型偷懶,會留下「杯葛 / 超級電腦 / 資訊」這類轉了字卻沒換詞的台灣用語。

用法: python scripts/check_translation_locale.py <group> [<group> ...]
      不給參數則檢查全部 zh-hans 庫。

⚠ 這支只是**攔明顯漏網**,25 組詞對涵蓋不了全部。
   2026-09-01 實測 4 篇翻譯稿:自動掃描 0 命中,但人工讀才看見真正做對的地方
   (杯葛→阻挠、超級電腦→超级计算机、羅賓森→罗宾逊、通緝中的→遭到通缉的)。
   **結論:自動掃描過關不等於品質好,翻譯稿仍要人工讀一遍。**
"""
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from opencc import OpenCC
t2s = OpenCC('t2s').convert

# ⚠ 詞對表 2026-09-01 修過一次:第一版有 14 組是**錯規則**,全庫掃出 13 組全是誤報。
# 砍掉的錯規則與原因(別再加回來):
#   樂團→乐队   ✗「乐团」大陸完全通用(交响乐团、爱乐乐团),乐队專指搖滾樂團
#   團員→成员   ✗「团员」大陸通用(乐团团员)
#   影片→视频   ✗「影片」大陸指電影,完全通用
#   品質→质量 / 水準→水平 / 大廈→大楼 / 宵夜→夜宵 / 超級電腦→超级计算机
#              ✗ 右邊較常用,但左邊在大陸也通,不能當違規
#   影集→剧集   ✗ 語意本就不同(影集在大陸指相冊)
#   鳳梨/馬鈴薯/番茄 ✗ 大陸也用(马铃薯是學名)
#   夥伴→伙伴 / 神蹟→神迹 ✗ 轉字後即相同,規則本身無效
# 只保留「該詞轉成簡體後在大陸幾乎不用」的確定案例:
PAIRS = [('網路','网络'),('資訊','信息'),('計程車','出租车'),('腳踏車','自行车'),
         ('螢幕','屏幕'),('冷氣','空调'),('義大利','意大利'),('雪梨','悉尼'),
         ('杯葛','阻挠'),('訊號','信号'),('網誌','博客'),('隨身碟','U盘'),
         ('程式','程序'),('軟體','软件'),('硬體','硬件'),('滑鼠','鼠标')]
TRAD = ('為與這麼個們來對時後說產動務開關實現處點經濟會體區華書東馬車門長風飛'
        '陣陳際隨階雙難靜韓題顯驗驚讓認識語調議護讀變豐醫獸禮權歸歲歷')

d = json.load(io.open('data/synopses_library/zh-hans.json', encoding='utf-8'))
syn = d.get('syn', d)
groups = sys.argv[1:] or sorted(syn)
bad = 0
for g in groups:
    v = syn.get(g)
    t = v.get('zh-hans', '') if isinstance(v, dict) else ''
    if not t:
        print('  [!] 不在庫或無內文: %s' % g); continue
    issues = []
    for tw, cn in PAIRS:
        s = t2s(tw)
        if s != cn and s in t:
            issues.append('%s→%s(應為 %s)' % (tw, s, cn))
    left = sorted(set(c for c in t if c in TRAD))
    if left:
        issues.append('繁體殘留 ' + ''.join(left[:8]))
    if issues:
        bad += 1
        print('❌ %-36s %s' % (g[:36], ' / '.join(issues)))
print('\n檢查 %d 組 → %s' % (len(groups), '全部通過' if not bad else '%d 組有問題' % bad))
print('⚠ 提醒:自動掃描過關不等於品質好,翻譯稿仍要人工讀一遍。')
