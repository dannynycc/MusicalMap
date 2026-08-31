# -*- coding: utf-8 -*-
"""三語年份一致性 + 完整性檢查(歐陸原創)。

繁×簡的用字掃描抓不到「英文版單獨出錯」——英文是拉丁字母、中文是音譯,沒得比。
年份不受音譯影響,是唯一能橫跨三語的硬錨點。

⚠ 讀結果要小心兩類誤報(2026-09-01 實測):
  1. "1990s" / "early-1960s" 會被抓成 1990 / 1960 —— 不是年份矛盾
  2. 某語有、某語沒有 = 詳略差異,不是錯
真正該追的是「**只在單一語言出現的具體年份**」,順著它去讀上下文——
本次就是這樣從 elvalt nok klubja 的 EN "In 1969" 讀到同句的專名錯字 Xintia(應為 Cynthia)。
"""
import io,re,sys,json
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
def load(n):
    d=json.load(io.open('data/synopses_library/'+n,encoding='utf-8')); return d.get('syn',d)
en,zht,zhs=load('en.json'),load('zh-hant.json'),load('zh-hans.json')
EU=sorted(json.load(io.open('scripts/qa/fixtures/euro_groups.json',encoding='utf-8')))
YR=re.compile(r'(?<!\d)(1[0-9]{3}|20[0-4][0-9])(?!\d)')
def body(d,g,k):
    v=d.get(g); return v.get(k,'') if isinstance(v,dict) else ''
miss=[];ydiff=[]
for g in EU:
    e,a,b=body(en,g,'en'),body(zht,g,'zh'),body(zhs,g,'zh-hans')
    lack=[n for n,v in (('en',e),('繁',a),('簡',b)) if not v]
    if lack: miss.append((g,lack)); continue
    ye,ya,yb=set(YR.findall(e)),set(YR.findall(a)),set(YR.findall(b))
    if len(set(map(frozenset,(ye,ya,yb))))>1: ydiff.append((g,sorted(ye),sorted(ya),sorted(yb)))
print('歐陸原創 %d 組;三語缺漏 %d 組;年份不一致 %d 組'%(len(EU),len(miss),len(ydiff)))
for g,l in miss: print('  缺 %-40s %s'%(g,l))
for g,e,a,b in ydiff:
    print('  %-40s EN:%-12s 繁:%-12s 簡:%s'%(g[:40],','.join(e) or '-',','.join(a) or '-',','.join(b) or '-'))
