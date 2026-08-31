# -*- coding: utf-8 -*-
"""線索蒐集(非判定):對每組的原作/原題,查各語維基是否有 zh 條目連結。
有 zh 條目 = 中文圈可能有通行名,值得深查;沒有 = 仍要用其他管道再查一輪。"""
import io,sys,json,time,urllib.request,urllib.parse
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
UA={'User-Agent':'MusicalMap-title-research/1.0 (dannynycc@gmail.com)'}
def api(lang,params):
    url='https://%s.wikipedia.org/w/api.php?%s'%(lang,urllib.parse.urlencode(dict(params,format='json')))
    return json.loads(urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=25).read().decode('utf-8'))
def zh_of(lang,title):
    try:
        d=api(lang,{'action':'query','prop':'langlinks','lllang':'zh','lllimit':'5','redirects':'1','titles':title})
        for pid,p in d.get('query',{}).get('pages',{}).items():
            if pid=='-1': return ('無此條目',None)
            for l in p.get('langlinks',[]): return (p.get('title'),l['*'])
            return (p.get('title'),None)
    except Exception as e: return ('err:%s'%e,None)
    return ('?',None)
def search(lang,q):
    try:
        d=api(lang,{'action':'query','list':'search','srsearch':q,'srlimit':'3'})
        return [x['title'] for x in d.get('query',{}).get('search',[])]
    except Exception: return []
ITEMS=json.load(open(sys.argv[1],encoding='utf-8'))
for grp,lang,title in ITEMS:
    art,zh = zh_of(lang,title)
    line='%-34s %s:%-40s -> %-34s zh=%s'%(grp,lang,title[:40],str(art)[:34],zh or '—')
    if not zh:
        line += '   [搜尋候選] '+' | '.join(search(lang,title))[:110]
    print(line,flush=True)
    time.sleep(0.25)
