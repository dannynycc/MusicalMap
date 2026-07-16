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
      date:'2021-11-20', time:'13:00', venue:'JR East Shiki Theatre Umi JR東日本四季劇場[海]', city:'Tokyo', country:'Japan', cc:'JP',
      lat:35.6310, lng:139.7760, seat:'S席 12列', price:12000, cur:'JPY', rating:4.5, fav:false, era:'modern', scale:'spectacle',
      note:'Friend Like Me 的換裝魔術看不懂怎麼辦到的。' },
    { id:10, title:'Les Misérables', zh:'悲慘世界', prod:'東宝', color:'#B8242A',
      date:'2021-11-23', time:'17:30', venue:'Imperial Theatre 帝国劇場', city:'Tokyo', country:'Japan', cc:'JP',
      lat:35.6760, lng:139.7620, seat:'A席 5列', price:14000, cur:'JPY', rating:4.5, fav:false, era:'classic', scale:'spectacle',
      note:'日語版的 Stars 別有味道。' },
    { id:11, title:'Elisabeth', zh:'伊麗莎白', prod:'東宝', color:'#5B4B8A',
      date:'2024-06-15', time:'12:00', venue:'Imperial Theatre 帝国劇場', city:'Tokyo', country:'Japan', cc:'JP',
      lat:35.6760, lng:139.7620, seat:'S席 8列', price:13500, cur:'JPY', rating:5, fav:true, era:'classic', scale:'spectacle',
      note:'死神 Der Tod 一出場全場尖叫。' },
    { id:12, title:'Wicked', zh:'女巫前傳', prod:'한국 프로덕션', color:'#2E8B57',
      date:'2023-09-10', time:'14:00', venue:'샤롯데씨어터 Charlotte Theater', city:'Seoul', country:'South Korea', cc:'KR',
      lat:37.5110, lng:127.1030, seat:'VIP R 3열', price:150000, cur:'KRW', rating:4, fav:false, era:'modern', scale:'spectacle',
      note:'韓版 Elphaba 高音炸裂。' },
    { id:13, title:'Dear Evan Hansen', zh:'親愛的艾文漢森', prod:'巡演', color:'#1F6FEB',
      date:'2022-11-12', time:'19:30', venue:'National Theater and Concert Hall 國家戲劇院', city:'Taipei', country:'Taiwan', cc:'TW',
      lat:25.0400, lng:121.5170, seat:'2樓 5排 12號', price:2800, cur:'TWD', rating:4.5, fav:false, era:'modern', scale:'intimate',
      note:'You Will Be Found 哭到不行。' },
    { id:14, title:"Spring Awakening", zh:'春之覺醒', prod:'本地製作', color:'#88B04B',
      date:'2023-05-20', time:'14:30', venue:'Taipei Performing Arts Center 臺北表演藝術中心', city:'Taipei', country:'Taiwan', cc:'TW',
      lat:25.0810, lng:121.5260, seat:'1樓 8排', price:2400, cur:'TWD', rating:4, fav:false, era:'modern', scale:'intimate',
      note:'中文版改編比想像中好。' },
    { id:15, title:'Cats', zh:'貓', prod:'巡演', color:'#D4A017',
      date:'2024-08-03', time:'14:30', venue:'National Theater and Concert Hall 國家戲劇院', city:'Taipei', country:'Taiwan', cc:'TW',
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
  // demo 劇種傳統(tag):真實紀錄由 catalog 對映烤入;demo 手動補(全英美系,除了 Elisabeth=德奧)
  shows.forEach(s => { if (s.tag == null) s.tag = 'Broadway/West End'; });
  shows[10].tag = '德奧音樂劇';   // id:11 Elisabeth

  const WEEKDAYS = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'];
  const WEEKDAYS_ZH = ['日','一','二','三','四','五','六'];
  const MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];

  // wd 只對「完整日期(YYYY-MM-DD)」有意義:new Date('2026T…')=1/1(週四)、new Date('2026-03T…')=該月1號,
  // 只填年/年月的紀錄會被灌進「各星期」某個假星期(年→全算週四)。回 -1 讓 perWeekday 排除(2026-07-10)。
  function wd(d){ return (d && d.length >= 10) ? new Date(d+'T00:00:00').getDay() : -1; }
  function yr(d){ return d.slice(0,4); }
  function mo(d){ return parseInt(d.slice(5,7),10)-1; }

  // ── 已看(過去) vs 即將(未來)：用「場次日期 vs 今天」判定，不改 DB schema ──
  // 部分日期用「該粒度最早一天」判「即將」：年精度 YYYY→1/1、月精度 YYYY-MM→當月1日、日精度直接比。
  // 「即將上演」= 整段日期都晚於今天才算;個人足跡預設記的是看過的,只填「當年年份」(如今年 2026)=已看,
  // 不再被誤標即將(舊版補到期末 YYYY-12-31→當年只填年份被判未來=bug)。當天(=今天)算「已看」。
  // 未來年份(如 2027→2027-01-01)仍正確判為即將;當年未來月份(如 2026-11→2026-11-01)也仍是即將。
  function todayStr(){ const d=new Date(); const p=n=>String(n).padStart(2,'0');
    return d.getFullYear()+'-'+p(d.getMonth()+1)+'-'+p(d.getDate()); }
  function normStart(d){ if(!d)return '';
    if(d.length===4)return d+'-01-01';
    if(d.length===7)return d+'-01';
    return d; }
  function isFuture(d){ return !!d && normStart(d) > todayStr(); }   // 最早可能日都晚於今天才算即將
  // 非未來=已看,含「無日期」(記了卻沒填時間=看過但不記得哪天,仍是已看)。
  // 舊版 isPast('')=false → 無日期紀錄既非過去也非未來:hero 大數字(stats('past'))漏算它,
  // 但海報牆(全 S)與護照蓋章(!isFuture)有算 → 同頁數字兜不攏(2026-07-10)。與 !isFuture 對齊。
  function isPast(d){ return !isFuture(d); }
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
      firstDate: src.map(s=>s.date).filter(Boolean).sort()[0],   // 空日期('')會排最前毒化「首演年」徽章(2026-07-15 修)
      lastDate: src.map(s=>s.date).filter(Boolean).sort().slice(-1)[0],
      upcoming: shows.filter(s=>isFuture(s.date)).length,   // 即將 N 場
    };
  }

  // 國家→洲(劇迷類型的地理廣度軸)。音樂劇重鎮叢聚少數洲板塊,「環球」以跨洲數認定
  // 而非國數(台日韓中 4 國同在亞洲≠環球,2026-07-13 調查定案)。鍵同時涵蓋 catalog
  // 短名(UK/USA)與 normCountry 後的全名,me.html/u-view 兩邊餵進來的值都吃。
  const CONT = {
    'USA':'NA','United States':'NA','US':'NA','Canada':'NA','Mexico':'NA',
    'Brazil':'SA','Argentina':'SA','Chile':'SA','Peru':'SA','Colombia':'SA',
    'UK':'EU','United Kingdom':'EU','Ireland':'EU','France':'EU','Germany':'EU','Austria':'EU',
    'Switzerland':'EU','Spain':'EU','Portugal':'EU','Italy':'EU','Netherlands':'EU','Belgium':'EU',
    'Sweden':'EU','Norway':'EU','Denmark':'EU','Finland':'EU','Poland':'EU','Czech Republic':'EU',
    'Hungary':'EU','Greece':'EU','Slovenia':'EU','Romania':'EU','Croatia':'EU','Slovakia':'EU',
    'Estonia':'EU','Latvia':'EU','Lithuania':'EU','Bulgaria':'EU','Serbia':'EU','Russia':'EU',
    'Ukraine':'EU','Jersey':'EU',
    'Taiwan':'AS','Japan':'AS','South Korea':'AS','Korea':'AS','China':'AS','Hong Kong':'AS',
    'Macau':'AS','Singapore':'AS','Malaysia':'AS','Thailand':'AS','Philippines':'AS',
    'Indonesia':'AS','Vietnam':'AS','India':'AS','Israel':'AS','Turkey':'AS',
    'United Arab Emirates':'AS','UAE':'AS',
    'Australia':'OC','New Zealand':'OC',
    'South Africa':'AF','Egypt':'AF',
    // 2026-07-15 補漏:缺席國家會「算國數不算洲數」,低估環球旅人 persona
    'Iceland':'EU','Luxembourg':'EU','Malta':'EU','Cyprus':'EU','Monaco':'EU','Andorra':'EU',
    'Bosnia and Herzegovina':'EU','North Macedonia':'EU','Albania':'EU','Montenegro':'EU','Belarus':'EU','Moldova':'EU',
    'Qatar':'AS','Saudi Arabia':'AS','Kuwait':'AS','Bahrain':'AS','Oman':'AS','Jordan':'AS','Lebanon':'AS',
    'Kazakhstan':'AS','Uzbekistan':'AS','Sri Lanka':'AS','Bangladesh':'AS','Pakistan':'AS','Nepal':'AS',
    'Mongolia':'AS','Cambodia':'AS','Laos':'AS','Myanmar':'AS','Brunei':'AS',
    'Costa Rica':'NA','Panama':'NA','Guatemala':'NA','Puerto Rico':'NA','Dominican Republic':'NA','Cuba':'NA','Jamaica':'NA',
    'Uruguay':'SA','Paraguay':'SA','Bolivia':'SA','Ecuador':'SA','Venezuela':'SA',
    'Morocco':'AF','Tunisia':'AF','Kenya':'AF','Nigeria':'AF','Ghana':'AF','Zimbabwe':'AF','Namibia':'AF',
  };

  // 「你是什麼樣的劇迷」— 三條真資料軸,連續光譜(只看已發生的場次)。
  // 舊版問題(2026-07-13 重設計):era/scale 軸只有 demo 有資料=真人永遠看不到;
  // 「≥4 國=環球旅人」同洲也算環球;滑桿只有 14/86 兩檔假裝連續。全部換掉。
  function personality(){
    const past = pick('past');
    const st = stats('past');
    // i18n:頁面有載 js/mm-strings.js 就用其字典;沒載沿用中文字面
    const L=(k,zh)=>{ if(window.MM_T){const v=window.MM_T(k); if(v&&v!==k)return v;} return zh; };
    const LN=(k,zh,vars)=>{ let s=L(k,zh); Object.entries(vars||{}).forEach(([n,v])=>{ s=s.replace('{'+n+'}',v); }); return s; };
    // 完全沒有「看過」的紀錄才擋(0 場沒東西可畫)→ 鼓勵句;1 場起就畫五邊形(2026-07-16 使用者:低端也要有形狀+鼓勵)
    if(past.length === 0){
      return { enough:false, code:'', nickname:'', axes:[],
        aura:(past[0]||shows[0]||{}).color||'#7c5cff', aura2:'#6A0DAD',
        blurb: L('p_none','看完你的第一部音樂劇，這裡就會浮現屬於你的劇迷五邊形！') };
    }
    const clampPos = p => Math.max(6, Math.min(94, Math.round(p)));   // 圓點半徑內縮,貼邊不出血
    const axes = [], nick = [], parts = [];

    // ── 軸1 地理廣度:洲數為主、國數為輔,5 檔 ──
    const ctry = new Set(past.map(s=>s.country).filter(Boolean));
    const cont = new Set([...ctry].map(c=>CONT[c]||'').filter(Boolean));
    const nC = ctry.size, nK = cont.size;
    const geoT = nK>=3 ? 4 : nK===2 ? 3 : nC>=3 ? 2 : nC===2 ? 1 : 0;
    const GEO = [L('p_geo0','在地扎根'),L('p_geo1','跨境嚐鮮'),L('p_geo2','區域旅人'),L('p_geo3','洲際旅人'),L('p_geo4','環球旅人')];
    axes.push([GEO[0], GEO[4], clampPos([8,29,50,71,92][geoT]),
      GEO[geoT]+' · '+LN('p_geo_ev','{n} 國 · {m} 洲',{n:nC,m:nK})]);
    nick.push(GEO[geoT]);
    parts.push([
      L('p_geo_b0','足跡都在同一個國家'),
      L('p_geo_b1','已經跨出國門看戲'),
      LN('p_geo_b2','你在 {n} 個國家看過戲，把一整個區域當主場',{n:nC}),
      LN('p_geo_b3','足跡橫跨 {m} 大洲',{m:nK}),
      LN('p_geo_b4','足跡橫跨 {m} 大洲，名副其實看遍世界',{m:nK}),
    ][geoT]);

    // ── 軸2 重看習性:4 檔+最小樣本護欄(總場次<5 小樣本噪音大,不發此軸) ──
    const rate = st.total ? 1 - st.unique/st.total : 0;
    const maxRep = st.topShows.length ? st.topShows[0][1] : 0;
    let repT = -1;
    if(st.total >= 5){
      repT = (rate>0.5 || maxRep>=5) ? 3 : rate>=0.3 ? 2 : rate>=0.1 ? 1 : 0;
      const REP = [L('p_rep0','嚐鮮探索'),L('p_rep1','回頭客'),L('p_rep2','念舊死忠'),L('p_rep3','N 刷狂熱')];
      let pos = clampPos(rate/0.6*88 + 6);                       // 重看率 0→6%、60%+→94%,連續定位
      if(repT===3) pos = Math.max(pos, 85);                      // 單劇 ≥5 刷即狂熱,位置跟上檔位
      const ev = (repT===3 && maxRep>=5)
        ? LN('p_rep_ev_max','同一齣刷了 {x} 次',{x:maxRep})
        : LN('p_repeat','重看率 {n}%',{n:Math.round(rate*100)});
      axes.push([REP[0], REP[3], pos, REP[repT]+' · '+ev]);
      nick.push(REP[repT]);
      parts.push([
        L('p_rep_b0','幾乎每齣都嚐鮮'),
        L('p_rep_b1','偶爾為愛回鍋'),
        L('p_rep_b2','願意為愛的戲二刷三刷'),
        LN('p_rep_b3','同一齣可以刷上 {x} 次',{x:Math.max(maxRep,5)}),
      ][repT]);
    }

    // ── 軸3 劇種口味:英美主流 vs 其他傳統(catalog tag 烤入;有 tag 的 ≥3 場才發) ──
    const tagged = past.filter(s=>s.tag);
    if(tagged.length >= 3){
      const anglo = tagged.filter(s=>s.tag==='Broadway/West End').length;
      const ratio = anglo/tagged.length;
      const tradT = ratio>=0.7 ? 0 : ratio>0.3 ? 1 : 2;
      const TRAD = [L('p_trad0','英美主流派'),L('p_trad1','跨界雜食'),L('p_trad2','多元劇種迷')];
      axes.push([L('p_trad_l','英美主流'), L('p_trad_r','多元劇種'), clampPos((1-ratio)*100),
        TRAD[tradT]+' · '+LN('p_trad_ev','英美 {a} / 其他 {b}',{a:anglo,b:tagged.length-anglo})]);
      if(nick.length<2) nick.push(TRAD[tradT]);
      parts.push([
        L('p_trad_b0','口味以英美主流為本'),
        L('p_trad_b1','英美與各國原創都吃'),
        L('p_trad_b2','偏愛英美之外的各國劇種'),
      ][tradT]);
    }

    // ── 五邊形戰力圖(2026-07-16):5 軸各取不同資料維度,盡量不重疊;值 0–100 ──
    const _tagged = past.filter(s=>s.tag);
    const _dTags = new Set(_tagged.map(s=>s.tag)).size;
    const _nAnglo = _tagged.filter(s=>s.tag!=='Broadway/West End').length;
    const _wRatio = _tagged.length ? _nAnglo/_tagged.length : 0;
    const _pyrs = [...new Set(past.map(s=>s.date&&s.date.slice(0,4)).filter(Boolean))].map(Number);
    const _span = _pyrs.length ? Math.max(..._pyrs)-Math.min(..._pyrs)+1 : 0;
    // 前段快、後段慢(對數前載):第 1 部就有感(~19%),每多一部遞增量遞減——不用線性(2026-07-16 使用者)
    const _fl = (x, cap) => x<=0 ? 0 : Math.min(100, 100*Math.log(1+x)/Math.log(1+cap));
    const _vExplore = Math.round(_fl(st.unique, 40));                                                // 探索者:不重複劇目(1→19% 2→30% 3→37%)
    const _vGenre   = Math.min(100, Math.round(_fl(_dTags, 5)*0.82 + _wRatio*18));                   // 世界劇種通:劇種多樣(前載)+世界性
    const _vGlobal  = Math.min(100, Math.round(_fl(nC + Math.max(0,nK-1)*2, 12)));                   // 環球玩家:國數+跨洲加權(前載)
    const _vLoyal   = Math.min(100, Math.round(_fl(rate*10 + Math.max(0,maxRep-1)*1.5, 12)));        // 忠誠鐵粉:重看強度(沒重看=0,前載)
    const _vVet     = Math.min(100, Math.round(_fl(_span,13)*0.62 + _fl(Math.min(st.total,120),50)*0.38)); // 資深老手:年跨度(前載)+總量
    // 每軸:名稱 nm、這軸在算什麼 ds、你的實績 ev、分數 v(0–100);供雷達圖 + 解釋清單共用
    const radar = { items: [
      { nm:L('pr_explorer','探索者'),   ds:L('pr_explorer_d','看過多少不同作品'),     ev:LN('pr_ev_explorer','{n} 部不同作品',{n:st.unique}),        v:_vExplore },
      { nm:L('pr_genre','世界劇種通'),  ds:L('pr_genre_d','涉獵多少不同劇種傳統'),     ev:(_dTags?LN('pr_ev_genre','{n} 種劇種',{n:_dTags}):L('pr_ev_genre0','尚無劇種標記')), v:_vGenre },
      { nm:L('pr_global','環球玩家'),   ds:L('pr_global_d','足跡跨越多少國家與大洲'),  ev:LN('pr_ev_global','{n} 國 · {m} 洲',{n:nC,m:nK}),          v:_vGlobal },
      { nm:L('pr_loyal','忠誠鐵粉'),    ds:L('pr_loyal_d','為愛的戲重看的程度'),       ev:(maxRep>=2?LN('pr_ev_loyal','最多 {n} 刷',{n:maxRep}):L('pr_ev_loyal0','尚未重看')), v:_vLoyal },
      { nm:L('pr_veteran','資深老手'),  ds:L('pr_veteran_d','看戲資歷有多深'),         ev:LN('pr_ev_veteran','橫跨 {n} 年',{n:_span}),               v:_vVet },
    ] };
    return {
      enough:true,
      code:'', nickname: nick.join(' · '),   // 間隔號用「·」(「・」是日文中黑,台灣不用)
      aura: (past[0]||shows[0]||{}).color||'#7c5cff', aura2: '#6A0DAD',
      axes,   // [左端, 右端, pos(6–94 連續), 檔名+實證數字]
      radar,  // 五邊形戰力圖 {items:[{nm,ds,ev,v}×5]}
      blurb: parts.join(L('p_sep','，')) + L('p_end','。'),
      // 剛起步(<5 場)給鼓勵句,五邊形還小是正常的,鼓勵繼續收集(2026-07-16)
      encourage: (st.total < 5) ? L('p_grow','才剛起步——每多看一部、去一個新城市、重刷一次愛劇，五邊形就會再長大一塊。慢慢養出只屬於你的形狀吧！') : '',
    };
  }

  // 成就徽章(me/u 共用計算;文案由頁面 i18n 渲染)。徽章=跨過門檻的事件,精確統計
  // 數字留統計區;續級門檻讓高活躍用戶永遠有下一級(2026-07-13 重設計)。
  // 回傳每族 {key, value, tier(-1=未解鎖), reached(已達門檻), next(下一門檻), extra}
  function badges(){
    const past = pick('past');
    const st = stats('past');
    const dayCount = {};
    past.forEach(s=>{ if(s.date && s.date.length>=10) dayCount[s.date]=(dayCount[s.date]||0)+1; });
    const doubleDays = Object.values(dayCount).filter(n=>n>=2).length;
    const yrs = [...new Set(past.map(s=>s.date&&s.date.slice(0,4)).filter(Boolean))].map(Number).sort((a,b)=>a-b);
    let run = yrs.length?1:0, bestRun = run;
    for(let i=1;i<yrs.length;i++){ run = (yrs[i]===yrs[i-1]+1) ? run+1 : 1; bestRun = Math.max(bestRun, run); }
    const maxRep = st.topShows.length ? st.topShows[0][1] : 0;
    const topTitle = st.topShows.length ? st.topShows[0][0] : '';
    const firstYear = st.firstDate ? st.firstDate.slice(0,4) : '';
    // ── 9 族新成就(2026-07-15;皆從既有欄位算,無需新資料)──
    const fiveStar = past.filter(s=>s.rating===5).length;                          // N1 五星鑑賞家
    const reviews  = past.filter(s=>s.note && String(s.note).trim()).length;       // N2 劇評人
    const faves    = past.filter(s=>s.fav).length;                                 // N3 心頭好
    const traditions = new Set(past.map(s=>s.tag).filter(Boolean)).size;           // N4 劇種雜食(不同劇種傳統)
    const _vc={}; past.forEach(s=>{ if(s.venue) _vc[s.venue]=(_vc[s.venue]||0)+1; });
    const regular  = Object.values(_vc).length ? Math.max(...Object.values(_vc)) : 0;  // N5 劇院常客(同館最多場)
    const _ym={};  past.forEach(s=>{ if(s.date&&s.date.length>=7) _ym[s.date.slice(0,7)]=(_ym[s.date.slice(0,7)]||0)+1; });
    const marathon = Object.values(_ym).length ? Math.max(...Object.values(_ym)) : 0;  // N6 馬拉松月(單月最多場)
    const veteran  = yrs.length ? (yrs[yrs.length-1]-yrs[0]+1) : 0;                 // N7 資深劇迷(年跨度)
    const _tc={};  past.forEach(s=>{ if(s.title&&s.city){ (_tc[s.title]=_tc[s.title]||new Set()).add(s.city); } });
    const crossCity = Object.values(_tc).length ? Math.max(...Object.values(_tc).map(x=>x.size)) : 0;  // N8 追劇跨城
    const watchlist = st.upcoming || 0;                                            // N9 口袋名單(未來場次)
    const DEFS = [
      { key:'first',     v: st.total>=1?1:0, tiers:[1],                  extra:firstYear },
      { key:'shows',     v: st.total,        tiers:[5,10,25,50,100,200] },
      { key:'countries', v: st.countries,    tiers:[2,3,5,8]            },
      { key:'cities',    v: st.cities,       tiers:[3,8,15,25]          },
      { key:'works',     v: st.unique,       tiers:[10,25,50,100]       },
      { key:'devotee',   v: maxRep,          tiers:[3,5,10],            extra:topTitle },
      { key:'double',    v: doubleDays,      tiers:[1,3,5]              },
      { key:'streak',    v: bestRun,         tiers:[2,3,5]              },
      { key:'fivestar',  v: fiveStar,        tiers:[3,10,25]            },
      { key:'reviews',   v: reviews,         tiers:[3,10,25]            },
      { key:'faves',     v: faves,           tiers:[3,10,20]            },
      { key:'traditions',v: traditions,      tiers:[2,3,4]              },
      { key:'regular',   v: regular,         tiers:[3,5,10]             },
      { key:'marathon',  v: marathon,        tiers:[3,5,8]              },
      { key:'veteran',   v: veteran,         tiers:[5,10,15]            },
      { key:'crosscity', v: crossCity,       tiers:[2,3]                },
      { key:'watchlist', v: watchlist,       tiers:[1,3,5]              },
    ];
    return DEFS.map(d=>{
      let t = -1;
      d.tiers.forEach((th,i)=>{ if(d.v>=th) t=i; });
      return { key:d.key, value:d.v, tier:t,
        reached: t>=0 ? d.tiers[t] : null,
        next: (t+1<d.tiers.length) ? d.tiers[t+1] : null,
        extra: d.extra||'' };
    });
  }

  // recent feed (newest first)；pastOnly=true 只取已發生的（餵「最新一場」）
  function recent(pastOnly){ const src = pastOnly?shows.filter(s=>isPast(s.date)):shows; return [...src].sort((a,b)=>b.date.localeCompare(a.date)); }
  // chronological route for the map polyline
  function route(){ return [...shows].sort((a,b)=>a.date.localeCompare(b.date)); }

  return { shows, stats, personality, badges, recent, route, isPast, isFuture, WEEKDAYS, WEEKDAYS_ZH, MONTHS, countBy };
})();
