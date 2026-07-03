/* ============================================================================
   My Musicals — DEMO sample data + stats helpers  (shared by all demo skins)
   This is throwaway demo data. Production reads the same shape from Supabase.
   Posters here are intentionally CSS-gradient placeholders (field `color`);
   in production each show carries a real poster image URL.
   ========================================================================== */
window.MM = (function () {
  // ---- sample log: one fan, 22 shows, 6 countries, 2021–2025 ----------------
  const shows = [
    { id:1,  title:'Hamilton', zh:'漢密爾頓', prod:'West End', color:'#C9A227',
      date:'2023-03-14', time:'19:30', venue:"Victoria Palace Theatre", city:'London', country:'United Kingdom', cc:'GB',
      lat:51.4965, lng:-0.1416, seat:'Stalls A12', price:89, cur:'GBP', rating:5, fav:true, era:'modern', scale:'spectacle',
      note:'第一次現場聽 My Shot，雞皮疙瘩。' },
    { id:2,  title:'Wicked', zh:'女巫前傳', prod:'West End', color:'#2E8B57',
      date:'2023-03-16', time:'14:30', venue:'Apollo Victoria Theatre', city:'London', country:'United Kingdom', cc:'GB',
      lat:51.4954, lng:-0.1430, seat:'Grand Circle B5', price:65, cur:'GBP', rating:4.5, fav:true, era:'modern', scale:'spectacle',
      note:'Defying Gravity 升空那刻全場屏息。' },
    { id:3,  title:'Les Misérables', zh:'悲慘世界', prod:'West End', color:'#B8242A',
      date:'2023-03-18', time:'19:30', venue:'Sondheim Theatre', city:'London', country:'United Kingdom', cc:'GB',
      lat:51.5117, lng:-0.1318, seat:'Stalls C8', price:95, cur:'GBP', rating:5, fav:true, era:'classic', scale:'spectacle',
      note:'One Day More 結尾差點站起來。' },
    { id:4,  title:'The Phantom of the Opera', zh:'歌劇魅影', prod:'West End', color:'#8E1C2E',
      date:'2023-03-21', time:'19:30', venue:"His Majesty's Theatre", city:'London', country:'United Kingdom', cc:'GB',
      lat:51.5089, lng:-0.1320, seat:'Royal Circle D3', price:110, cur:'GBP', rating:5, fav:false, era:'classic', scale:'spectacle',
      note:'吊燈墜落還是會被嚇到。' },
    { id:5,  title:'The Lion King', zh:'獅子王', prod:'Broadway', color:'#E67E22',
      date:'2022-07-02', time:'20:00', venue:'Minskoff Theatre', city:'New York', country:'United States', cc:'US',
      lat:51.0,  lng:0, seat:'Orchestra F11', price:159, cur:'USD', rating:4.5, fav:true, era:'modern', scale:'spectacle',
      note:'開場 Circle of Life，動物從觀眾席走出。' },
    { id:6,  title:'Moulin Rouge!', zh:'紅磨坊', prod:'Broadway', color:'#C0144F',
      date:'2022-07-04', time:'20:00', venue:'Al Hirschfeld Theatre', city:'New York', country:'United States', cc:'US',
      lat:40.7596, lng:-73.9897, seat:'Mezzanine A1', price:189, cur:'USD', rating:5, fav:true, era:'modern', scale:'spectacle',
      note:'整間劇院變成紅磨坊，太浮誇我愛。' },
    { id:7,  title:'Hadestown', zh:'冥界', prod:'Broadway', color:'#B5651D',
      date:'2022-07-06', time:'19:00', venue:'Walter Kerr Theatre', city:'New York', country:'United States', cc:'US',
      lat:40.7589, lng:-73.9869, seat:'Orchestra G14', price:145, cur:'USD', rating:5, fav:true, era:'modern', scale:'intimate',
      note:'Wait For Me 的燈泡擺動，神。' },
    { id:8,  title:'Six', zh:'六位皇后', prod:'Broadway', color:'#6A0DAD',
      date:'2022-07-08', time:'19:00', venue:'Lena Horne Theatre', city:'New York', country:'United States', cc:'US',
      lat:40.7590, lng:-73.9870, seat:'Orchestra D5', price:129, cur:'USD', rating:4, fav:false, era:'modern', scale:'intimate',
      note:'演唱會式音樂劇，超嗨。' },
    { id:9,  title:'Aladdin', zh:'阿拉丁', prod:'劇団四季', color:'#1F9E89',
      date:'2021-11-20', time:'13:00', venue:'JR東日本四季劇場[海]', city:'Tokyo', country:'Japan', cc:'JP',
      lat:35.6310, lng:139.7760, seat:'S席 12列', price:12000, cur:'JPY', rating:4.5, fav:false, era:'modern', scale:'spectacle',
      note:'Friend Like Me 的換裝魔術看不懂怎麼辦到的。' },
    { id:10, title:'Les Misérables', zh:'悲慘世界', prod:'東宝', color:'#B8242A',
      date:'2021-11-23', time:'17:30', venue:'帝国劇場', city:'Tokyo', country:'Japan', cc:'JP',
      lat:35.6760, lng:139.7620, seat:'A席 5列', price:14000, cur:'JPY', rating:4.5, fav:false, era:'classic', scale:'spectacle',
      note:'日語版的 Stars 別有味道。' },
    { id:11, title:'Elisabeth', zh:'伊麗莎白', prod:'東宝', color:'#5B4B8A',
      date:'2024-06-15', time:'12:00', venue:'帝国劇場', city:'Tokyo', country:'Japan', cc:'JP',
      lat:35.6760, lng:139.7620, seat:'S席 8列', price:13500, cur:'JPY', rating:5, fav:true, era:'classic', scale:'spectacle',
      note:'死神 Der Tod 一出場全場尖叫。' },
    { id:12, title:'Wicked', zh:'女巫前傳', prod:'한국 프로덕션', color:'#2E8B57',
      date:'2023-09-10', time:'14:00', venue:'샤롯데씨어터 Charlotte Theater', city:'Seoul', country:'South Korea', cc:'KR',
      lat:37.5110, lng:127.1030, seat:'VIP R 3열', price:150000, cur:'KRW', rating:4, fav:false, era:'modern', scale:'spectacle',
      note:'韓版 Elphaba 高音炸裂。' },
    { id:13, title:'Dear Evan Hansen', zh:'親愛的艾文漢森', prod:'巡演', color:'#1F6FEB',
      date:'2022-11-12', time:'19:30', venue:'國家戲劇院', city:'Taipei', country:'Taiwan', cc:'TW',
      lat:25.0400, lng:121.5170, seat:'2樓 5排 12號', price:2800, cur:'TWD', rating:4.5, fav:false, era:'modern', scale:'intimate',
      note:'You Will Be Found 哭到不行。' },
    { id:14, title:"Spring Awakening", zh:'春之覺醒', prod:'本地製作', color:'#88B04B',
      date:'2023-05-20', time:'14:30', venue:'臺北表演藝術中心', city:'Taipei', country:'Taiwan', cc:'TW',
      lat:25.0810, lng:121.5260, seat:'1樓 8排', price:2400, cur:'TWD', rating:4, fav:false, era:'modern', scale:'intimate',
      note:'中文版改編比想像中好。' },
    { id:15, title:'Cats', zh:'貓', prod:'巡演', color:'#D4A017',
      date:'2024-08-03', time:'14:30', venue:'國家戲劇院', city:'Taipei', country:'Taiwan', cc:'TW',
      lat:25.0400, lng:121.5170, seat:'2樓 3排', price:3200, cur:'TWD', rating:3.5, fav:false, era:'classic', scale:'spectacle',
      note:'Memory 現場聽還是值得。' },
    { id:16, title:'The Book of Mormon', zh:'摩門經', prod:'West End', color:'#2B86D4',
      date:'2023-03-19', time:'15:00', venue:'Prince of Wales Theatre', city:'London', country:'United Kingdom', cc:'GB',
      lat:51.5100, lng:-0.1320, seat:'Stalls H10', price:75, cur:'GBP', rating:4, fav:false, era:'modern', scale:'intimate',
      note:'笑到肚子痛，政治不正確的剛剛好。' },
    { id:17, title:'Cabaret', zh:'酒店', prod:'West End', color:'#B5179E',
      date:'2024-11-05', time:'19:30', venue:'Kit Kat Club (Playhouse Theatre)', city:'London', country:'United Kingdom', cc:'GB',
      lat:51.5085, lng:-0.1230, seat:'Table 7', price:130, cur:'GBP', rating:5, fav:true, era:'classic', scale:'intimate',
      note:'進場就是沉浸式酒吧，太會了。' },
    { id:18, title:'Hamilton', zh:'漢密爾頓', prod:'Broadway', color:'#C9A227',
      date:'2024-02-09', time:'19:00', venue:'Richard Rodgers Theatre', city:'New York', country:'United States', cc:'US',
      lat:40.7592, lng:-73.9867, seat:'Orchestra K7', price:199, cur:'USD', rating:5, fav:true, era:'modern', scale:'spectacle',
      note:'朝聖原版卡司劇院，值回票價。' },
    { id:19, title:'Sweeney Todd', zh:'理髮師陶德', prod:'Broadway', color:'#6B6B6B',
      date:'2024-02-11', time:'14:00', venue:'Lunt-Fontanne Theatre', city:'New York', country:'United States', cc:'US',
      lat:40.7593, lng:-73.9847, seat:'Mezzanine C2', price:169, cur:'USD', rating:4.5, fav:false, era:'classic', scale:'intimate',
      note:'Sondheim 的和聲現場聽是另一個次元。' },
    { id:20, title:'König der Löwen', zh:'獅子王', prod:'Stage Entertainment', color:'#E67E22',
      date:'2025-01-18', time:'19:30', venue:'Stage Theater im Hafen', city:'Hamburg', country:'Germany', cc:'DE',
      lat:53.5430, lng:9.9690, seat:'Block 2 Reihe 7', price:120, cur:'EUR', rating:4, fav:false, era:'modern', scale:'spectacle',
      note:'坐渡輪去劇院本身就是體驗。' },
    { id:21, title:"Standing at the Sky's Edge", zh:'天際邊緣', prod:'West End', color:'#E07A5F',
      date:'2024-11-07', time:'19:30', venue:'Gillian Lynne Theatre', city:'London', country:'United Kingdom', cc:'GB',
      lat:51.5167, lng:-0.1206, seat:'Stalls D5', price:70, cur:'GBP', rating:4.5, fav:false, era:'modern', scale:'intimate',
      note:'Richard Hawley 的歌詞配上謝菲爾德的故事，意外動人。' },
    { id:22, title:'Hadestown', zh:'冥界', prod:'West End', color:'#B5651D',
      date:'2025-02-14', time:'19:30', venue:'Lyric Theatre', city:'London', country:'United Kingdom', cc:'GB',
      lat:51.5128, lng:-0.1330, seat:'Stalls F8', price:95, cur:'GBP', rating:5, fav:true, era:'modern', scale:'intimate',
      note:'情人節看 Orpheus & Eurydice，浪漫又心碎。' },
  ];
  // fix one stray coord (Lion King NYC)
  shows[4].lat = 40.7588; shows[4].lng = -73.9855;

  const WEEKDAYS = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'];
  const WEEKDAYS_ZH = ['日','一','二','三','四','五','六'];
  const MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];

  function wd(d){ return new Date(d+'T00:00:00').getDay(); }
  function yr(d){ return d.slice(0,4); }
  function mo(d){ return parseInt(d.slice(5,7),10)-1; }

  // ── 已看(過去) vs 即將(未來)：用「場次日期 vs 今天」判定，不改 DB schema ──
  // 部分日期採「該粒度最後一天」判定：年精度 YYYY→年底、月精度 YYYY-MM→月底、
  // 日精度直接比。當天(=今天)算「已看」。
  function todayStr(){ const d=new Date(); const p=n=>String(n).padStart(2,'0');
    return d.getFullYear()+'-'+p(d.getMonth()+1)+'-'+p(d.getDate()); }
  function normDate(d){ if(!d)return '';
    if(d.length===4)return d+'-12-31';
    if(d.length===7){const[y,m]=d.split('-');return y+'-'+m+'-'+String(new Date(+y,+m,0).getDate()).padStart(2,'0');}
    return d; }
  function isPast(d){ return !!d && normDate(d) <= todayStr(); }
  function isFuture(d){ return !!d && normDate(d) > todayStr(); }
  function pick(which){ return which==='past'?shows.filter(s=>isPast(s.date)) : which==='future'?shows.filter(s=>isFuture(s.date)) : shows; }

  function countBy(key, list){
    const src = list || shows;
    const m = new Map();
    src.forEach(s=>{ const k = (typeof key==='function')?key(s):s[key]; if(k===''||k==null)return; m.set(k,(m.get(k)||0)+1); });  // 空值不計（如「不記得城市」）
    return [...m.entries()].sort((a,b)=>b[1]-a[1]);
  }

  // which: 'all'(預設) | 'past'(只算已看) | 'future'(只算即將)
  function stats(which){
    const src = pick(which);
    const years = [...new Set(src.map(s=>yr(s.date)))].sort();
    const perYear = years.map(y=>[y, src.filter(s=>yr(s.date)===y).length]);
    const perMonth = MONTHS.map((m,i)=>[m, src.filter(s=>mo(s.date)===i).length]);
    const perWeekday = WEEKDAYS.map((w,i)=>[w, src.filter(s=>wd(s.date)===i).length]);
    const uniqueTitles = new Set(src.map(s=>s.title)).size;
    const spend = {};
    src.forEach(s=>{ spend[s.cur]=(spend[s.cur]||0)+s.price; });
    return {
      total: src.length,
      unique: uniqueTitles,
      countries: new Set(src.map(s=>s.country).filter(Boolean)).size,
      cities: new Set(src.map(s=>s.city).filter(Boolean)).size,
      venues: new Set(src.map(s=>s.venue).filter(Boolean)).size,
      years, perYear, perMonth, perWeekday,
      topShows: countBy('title', src),
      topCountries: countBy('country', src),
      topCities: countBy('city', src),
      topVenues: countBy('venue', src),
      favCount: src.filter(s=>s.fav).length,
      avgRating: src.length ? (src.reduce((a,s)=>a+s.rating,0)/src.length) : 0,
      spend,
      firstDate: src.map(s=>s.date).sort()[0],
      lastDate: src.map(s=>s.date).sort().slice(-1)[0],
      upcoming: shows.filter(s=>isFuture(s.date)).length,   // 即將 N 場
    };
  }

  // Spotify-Wrapped-style 4-letter "Theatregoer Personality"（只看已發生的場次）
  function personality(){
    const past = pick('past');
    const st = stats('past');
    const repeatRatio = st.total ? st.unique/st.total : 1;   // <0.85 → loyalist
    // era/scale 只有「劇庫範例」才有；使用者真實 mm-log 沒這欄 → 不假裝分析這兩軸
    const hasEra = past.some(s=>s.era==='modern'||s.era==='classic');
    const hasScale = past.some(s=>s.scale==='spectacle'||s.scale==='intimate');
    const modern = past.filter(s=>s.era==='modern').length;
    const classic = past.filter(s=>s.era==='classic').length;
    const spectacle = past.filter(s=>s.scale==='spectacle').length;
    const intimate = past.filter(s=>s.scale==='intimate').length;
    // i18n:頁面有載 js/mm-strings.js(公開頁 u.html)就用其字典;沒載(me.html)沿用中文字面
    const L=(k,zh)=>{ if(window.MM_T){const v=window.MM_T(k); if(v&&v!==k)return v;} return zh; };
    const LN=(k,zh,vars)=>{ let s=L(k,zh); Object.entries(vars||{}).forEach(([n,v])=>{ s=s.replace('{'+n+'}',v); }); return s; };
    const NAMES = {G:L('p_G','環球旅人'),L:L('p_L','在地常客'),Y:L('p_Y','念舊死忠'),X:L('p_X','嚐鮮探索'),M:L('p_M','當代派'),C:L('p_C','經典派'),S:L('p_S','大製作控'),I:L('p_I','小劇場魂')};
    const globe = st.countries>=4, loyal = repeatRatio<0.85;
    const axes = [
      [NAMES.G,NAMES.L, globe, LN('p_n_countries',`{n} 國`,{n:st.countries})],
      [NAMES.Y,NAMES.X, loyal, LN('p_repeat',`重看率 {n}%`,{n:Math.round((1-repeatRatio)*100)})],
    ];
    const nick = [NAMES[globe?'G':'L']];
    const parts = [
      globe ? LN('p_blurb_globe','你橫跨 {n} 國追劇',{n:st.countries})
            : (st.countries>1 ? LN('p_blurb_local_country','你在 {n} 個國家看過戲',{n:st.countries})
                              : LN('p_blurb_local_place','你在 {n} 個地方看過戲',{n:st.countries})),
      loyal ? L('p_blurb_loyal','願意為愛的戲二刷三刷') : L('p_blurb_fresh','幾乎每齣都嚐鮮'),
    ];
    if(hasEra){axes.push([NAMES.M,NAMES.C, modern>=classic, LN('p_axis_era','{m} 現代 / {c} 經典',{m:modern,c:classic})]);nick.push(NAMES[modern>=classic?'M':'C']);parts.push(modern>=classic?L('p_blurb_modern','口味偏當代'):L('p_blurb_classic','鍾情經典'));}
    if(hasScale){axes.push([NAMES.S,NAMES.I, spectacle>=intimate, LN('p_axis_scale','{s} 大 / {i} 小',{s:spectacle,i:intimate})]);nick.push(NAMES[spectacle>=intimate?'S':'I']);parts.push(spectacle>=intimate?L('p_blurb_spectacle','也擋不住大製作的聲光'):L('p_blurb_intimate','更愛小劇場的親密'));}
    if(nick.length<2)nick.push(NAMES[loyal?'Y':'X']);   // 沒有 era/scale 時用「重看率」補第二段暱稱
    const code = [globe?'G':'L', loyal?'Y':'X', hasEra?(modern>=classic?'M':'C'):'', hasScale?(spectacle>=intimate?'S':'I'):''].join('');
    return {
      code, nickname: nick.join(' · '),   // 間隔號用「·」(「・」是日文中黑,台灣不用)
      aura: (past[0]||shows[0]||{}).color||'#7c5cff', aura2: '#6A0DAD',
      axes,
      blurb: parts.join(L('p_sep','，')) + L('p_end','。'),
    };
  }

  // recent feed (newest first)；pastOnly=true 只取已發生的（餵「最新一場」）
  function recent(pastOnly){ const src = pastOnly?shows.filter(s=>isPast(s.date)):shows; return [...src].sort((a,b)=>b.date.localeCompare(a.date)); }
  // chronological route for the map polyline
  function route(){ return [...shows].sort((a,b)=>a.date.localeCompare(b.date)); }

  return { shows, stats, personality, recent, route, isPast, isFuture, WEEKDAYS, WEEKDAYS_ZH, MONTHS, countBy };
})();
