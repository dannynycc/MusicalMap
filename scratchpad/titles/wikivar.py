# -*- coding: utf-8 -*-
"""用 zh.wikipedia 地區詞轉換取得同一條目的『台灣正體 / 大陸簡體』標題。
注意:這只是**線索**,不是判定依據;最終仍要有出版品/媒體/官方來源佐證。"""
import io,sys,json,urllib.request,urllib.parse
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
UA={'User-Agent':'MusicalMap-title-research/1.0 (dannynycc@gmail.com)'}
def q(lang, title, variant):
    url='https://%s.wikipedia.org/w/api.php?%s'%(lang, urllib.parse.urlencode({
        'action':'query','format':'json','prop':'info','redirects':'1',
        'converttitles':'1','variant':variant,'titles':title}))
    r=urllib.request.Request(url,headers=dict(UA,**{'Accept-Language':variant}))
    d=json.loads(urllib.request.urlopen(r,timeout=25).read().decode('utf-8'))
    pages=d.get('query',{}).get('pages',{})
    out=[]
    for pid,p in pages.items():
        out.append((p.get('title'), pid!='-1'))
    return out
def langlink(fromlang, title, to='zh'):
    url='https://%s.wikipedia.org/w/api.php?%s'%(fromlang, urllib.parse.urlencode({
        'action':'query','format':'json','prop':'langlinks','lllang':to,'lllimit':'10',
        'redirects':'1','titles':title}))
    r=urllib.request.Request(url,headers=UA)
    d=json.loads(urllib.request.urlopen(r,timeout=25).read().decode('utf-8'))
    for pid,p in d.get('query',{}).get('pages',{}).items():
        for l in p.get('langlinks',[]): return l['*']
    return None
if __name__=='__main__':
    for arg in sys.argv[1:]:
        lang,title = arg.split(':',1) if ':' in arg and len(arg.split(':',1)[0])<=3 else ('zh',arg)
        zh = title if lang=='zh' else langlink(lang,title)
        print('== %s:%s  -> zh條目: %s'%(lang,title,zh))
        if zh:
            print('   zh-tw:',q('zh',zh,'zh-tw'))
            print('   zh-cn:',q('zh',zh,'zh-cn'))
