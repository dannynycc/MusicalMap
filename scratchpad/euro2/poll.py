# -*- coding: utf-8 -*-
import io,sys,time,urllib.request
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
MARK='遭篡位而失去王位的年輕君主哈倫'
URL='https://themusicalmap.com/data/synopses/zh-hant.json'
for i in range(60):
    try:
        req=urllib.request.Request(URL,headers={'User-Agent':'Mozilla/5.0','Cache-Control':'no-cache'})
        body=urllib.request.urlopen(req,timeout=30).read().decode('utf-8')
        if MARK in body:
            print('OK 正式站已更新 (第 %d 次輪詢, %s)'%(i+1,time.strftime('%H:%M:%S'))); sys.exit(0)
        print('[%d] 尚未更新 %s'%(i+1,time.strftime('%H:%M:%S')),flush=True)
    except Exception as e:
        print('[%d] err %s'%(i+1,e),flush=True)
    time.sleep(20)
print('TIMEOUT'); sys.exit(1)
