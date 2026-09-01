# -*- coding: utf-8 -*-
"""產生可貼進 javascript_tool 的批次抓取程式碼 —— URL 一律取自 data/shows.json 的真實 ticket_url。
🚨 存在的理由:2026-09-01 我一度自己拼湊 atrapalo 的 URL id,fetch 到完全不相干的頁面
   (哥本哈根導覽 / 塞維亞喜劇之夜 / Tudela 徒步導覽),差點把錯誤資料寫進帳本。
   有了這支,URL 由程式從資料取,結構上不可能編錯。
用法: python scratchpad/eses/genjs.py <host關鍵字> <起始index> <取幾個>
"""
import io,sys,json
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
host,start,n = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
lst=json.load(io.open('scratchpad/eses/list.json',encoding='utf-8'))
done=set()
try: done=set(json.load(io.open('scratchpad/eses/ledger.json',encoding='utf-8'))['items'])
except Exception: pass
sel=[v for v in lst if host in (v['url'] or '') and v['group'] not in done][start:start+n]
print('// 未查組數(此 host):%d,本批 %d 組'%(len([v for v in lst if host in (v['url'] or '') and v['group'] not in done]),len(sel)))
print('const P=%s;'%json.dumps([[v['group'],v['url']] for v in sel],ensure_ascii=False))
print(r"""const out=[];
for(const [g,u] of P){
  try{
    const r=await fetch(u,{credentials:'include'});
    const t=new DOMParser().parseFromString(await r.text(),'text/html').body.innerText;
    const i=t.search(/Descripci/i);
    out.push(g+' ['+r.status+'] :: '+(i>=0?t.slice(i+11,i+330):'(無描述)').replace(/\s+/g,' '));
  }catch(e){ out.push(g+' ERR '+String(e).slice(0,40)); }
  await new Promise(r=>setTimeout(r,700));
}
out.join(String.fromCharCode(10)+'---'+String.fromCharCode(10))""")
