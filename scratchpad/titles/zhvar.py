# -*- coding: utf-8 -*-
"""取得 zh.wikipedia 同一條目在【臺灣正體 zh-tw】與【大陸簡體 zh-cn】下的標題。
仍只是線索,最終要有出版品/媒體來源。"""
import io,sys,json,time,urllib.request,urllib.parse
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
UA={'User-Agent':'MusicalMap-title-research/1.0 (dannynycc@gmail.com)'}
def disp(title,variant):
    url='https://zh.wikipedia.org/w/api.php?'+urllib.parse.urlencode({
        'action':'parse','format':'json','page':title,'prop':'displaytitle|text',
        'variant':variant,'redirects':'1','disabletoc':'1'})
    try:
        d=json.loads(urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=30).read().decode('utf-8'))
        p=d.get('parse',{})
        import re
        dt=re.sub('<[^>]+>','',p.get('displaytitle','')) or p.get('title','')
        # 內文第一個粗體 = 條目主名(常含地區詞轉換)
        html=p.get('text',{}).get('*','')
        m=re.search(r'<b>(.{1,40}?)</b>',html)
        return dt, (re.sub('<[^>]+>','',m.group(1)) if m else '')
    except Exception as e:
        return 'err:%s'%e,''
for t in sys.argv[1:]:
    tw=disp(t,'zh-tw'); cn=disp(t,'zh-cn')
    print('%-16s  台灣正體: %-22s (首粗體 %s)' % (t, tw[0], tw[1]))
    print('%-16s  大陸簡體: %-22s (首粗體 %s)' % ('', cn[0], cn[1]))
    time.sleep(0.2)
