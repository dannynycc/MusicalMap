/* Public, read-only "My Musicals" — /u.html?u=<handle>.
 * Visually identical to me.html: it maps Supabase public_sightings rows into the
 * same MM.shows[] shape the owner view uses, then runs me.html's render script
 * verbatim (hero / poster wall / passport / log / map / stats / persona / detail).
 * No login, no editing: MM.shows is populated but document.documentElement.dataset.live
 * is never set, so the poster cards' edit/delete affordances stay hidden. */
(function () {
  const cfg = window.MM_CONFIG || {};

  /* ---- helpers shared by mapping + render ---- */
  const CCNORM = { 'UK': 'United Kingdom', 'USA': 'United States', 'US': 'United States', 'Korea': 'South Korea', 'U.S.': 'United States', 'U.K.': 'United Kingdom' };
  // 同館別名折疊(顯示層,不動資料):兩廳院戲劇院各種列名→國家戲劇院;臺中歌劇院含廳名→臺中國家歌劇院
  function foldVenue(v){ if(!v) return v;
    if(/國家戲劇院|国家戏剧院/.test(v)) return '國家戲劇院';
    if(/[臺台]中國家歌劇院|台中国家歌剧院|National Taichung Theater/i.test(v)) return '臺中國家歌劇院';
    return v; }
  window.MMFoldVenue = foldVenue;
  // 城市顯示統整(zh 介面):Taipei/台北→臺北 等官方「臺」字;en 介面保留英文
  function foldCity(c){ if(!c) return c;
    if((window.MM_HL||'zh-hant')==='en') return c;
    if(/^(taipei|台北|臺北)/i.test(c)) return '臺北';
    if(/^(taichung|台中|臺中)/i.test(c)) return '臺中';
    if(/^(tainan|台南|臺南)/i.test(c)) return '臺南';
    if(/^(kaohsiung|高雄)/i.test(c)) return '高雄';
    return c; }
  window.MMFoldCity = foldCity;
  // 場館名尾端帶「, 城市」「- NY」等冗餘後綴→顯示層剝除;與 me.html/pipeline 同規則(2026-07-15)
  // 官方名本身含城市的(Royal Opera House, Mumbai)白名單保留=忠實呈現
  window.MMStripCitySuffix = window.MMStripCitySuffix || function(v, city){ if(!v||!city) return v;
    if(/^(the )?royal opera house, mumbai$/i.test(String(v).trim())) return v;
    const ABBR={NY:'New York',NYC:'New York',LA:'Los Angeles',SF:'San Francisco',DC:'Washington'};
    const m=String(v).match(/\s*[,\-–—]\s*([A-Za-z .']+)$/); if(!m) return v;
    const suf=m[1].trim();
    if(suf.toLowerCase()===String(city).toLowerCase()||ABBR[suf.toUpperCase()]===city){
      const out=String(v).slice(0,m.index).replace(/[\s,\-–—]+$/,'');
      return out||v;
    }
    return v; };
  // 票價帶貨幣符號(與 me.html 同對照)
  window.MMFmtPrice = window.MMFmtPrice || function(p,c){ if(p==null||p==='') return '';
    const SYM={TWD:'NT$',USD:'$',GBP:'£',EUR:'€',JPY:'¥',KRW:'₩',CNY:'¥',HKD:'HK$',AUD:'A$',CAD:'C$',SGD:'S$',NZD:'NZ$',MXN:'MX$',BRL:'R$',CHF:'CHF',SEK:'kr',NOK:'kr',DKK:'kr',CZK:'Kč',HUF:'Ft',PLN:'zł'};
    const SUF=new Set(['kr','Kč','Ft','zł','CHF']);
    const s=SYM[c]; if(!s) return c?`${p} ${c}`:String(p);
    return SUF.has(s)?`${p} ${s}`:`${s}${p}`; };
  function normCountry(c) { return CCNORM[c] || c || ''; }

  function safeUrl(u) {
    if (!u) return null;
    try { const p = new URL(u, location.href); return ['http:', 'https:'].includes(p.protocol) ? p.href : null; }
    catch { return null; }
  }

  /* 公開頁 render 的是「別人」的收藏資料 → 所有進 innerHTML/屬性/SVG 的使用者欄位
     (劇名/劇院/城市/國家/座位…) 一律跳脫，擋 stored XSS。me.html 只 render 自己的
     資料所以原本沒跳脫；公開頁不能沿用那個假設。 */
  const esc = (v) => String(v == null ? '' : v).replace(/[&<>"']/g,
    (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

  /* i18n:UI 字串走 js/mm-strings.js 的 MM_T(?hl= 決定語言);en 模式下
     國家/城市/劇院名直接用資料原文(英文),不做中文在地化。 */
  const T = window.MM_T || ((k) => k);
  const MS = window.MM_S || ((x) => x);   // zh-hans:資料層地名(劇院/城市/國家)轉簡;其他語言 identity（避開 render 內的 S=MM.shows）
  const TN = (k, vars) => { let s = T(k); Object.entries(vars || {}).forEach(([n, v]) => { s = s.replace('{' + n + '}', v); }); return s; };
  const EN_UI = (window.MM_HL || 'zh-hant') === 'en';

  // 中文頁：國家名繁中；劇院名只取中文部分 + 去廳別後綴(大/中/小劇院…)、臺→台。
  const COUNTRY_ZH = { 'United States': '美國', 'USA': '美國', 'United Kingdom': '英國', 'UK': '英國', 'Taiwan': '台灣', 'Japan': '日本', 'South Korea': '南韓', 'China': '中國', 'Hong Kong': '香港', 'Macau': '澳門', 'Singapore': '新加坡', 'Australia': '澳洲', 'New Zealand': '紐西蘭', 'Canada': '加拿大', 'Germany': '德國', 'France': '法國', 'Austria': '奧地利', 'Switzerland': '瑞士', 'Spain': '西班牙', 'Italy': '義大利', 'Netherlands': '荷蘭', 'Belgium': '比利時', 'Sweden': '瑞典', 'Norway': '挪威', 'Denmark': '丹麥', 'Finland': '芬蘭', 'Ireland': '愛爾蘭', 'Poland': '波蘭', 'Czech Republic': '捷克', 'Hungary': '匈牙利', 'Portugal': '葡萄牙', 'Mexico': '墨西哥', 'Brazil': '巴西', 'Argentina': '阿根廷', 'United Arab Emirates': '阿聯', 'UAE': '阿聯', 'Philippines': '菲律賓', 'Malaysia': '馬來西亞', 'Thailand': '泰國', 'Indonesia': '印尼', 'India': '印度', 'Israel': '以色列', 'Turkey': '土耳其', 'South Africa': '南非', 'Russia': '俄羅斯', 'Vietnam': '越南', 'Ukraine': '烏克蘭', 'Bulgaria': '保加利亞', 'Chile': '智利', 'Colombia': '哥倫比亞', 'Croatia': '克羅埃西亞', 'Egypt': '埃及', 'Estonia': '愛沙尼亞', 'Greece': '希臘', 'Jersey': '澤西島', 'Latvia': '拉脫維亞', 'Lithuania': '立陶宛', 'Peru': '秘魯', 'Romania': '羅馬尼亞', 'Serbia': '塞爾維亞', 'Slovakia': '斯洛伐克', 'Slovenia': '斯洛維尼亞' };
  const countryZh = (c) => EN_UI ? (c || '') : MS(COUNTRY_ZH[c] || c || '');
  const _cjk = /[぀-ヿ㐀-鿿가-힯豈-﫿]/;
  const _HALL = new Set(['大劇院', '中劇院', '小劇院', '大劇場', '中劇場', '小劇場', '音樂廳', '演奏廳', '戲劇廳', '歌劇廳', '演藝廳', '表演廳', '實驗劇場', '排練場', '大廳', '小廳']);
  const venueZh = (v) => { if (!v) return v || '';
    if (EN_UI) { const en = String(v).split(/\s+/).filter((x) => !_cjk.test(x)).join(' ').trim(); return en || String(v); }   // en 模式抽英文部分;純中日韓館名無英文名→保留原文
    const t = String(v).split(/\s+/).filter((x) => _cjk.test(x)); if (!t.length) return MS(v); const core = t.filter((x) => !_HALL.has(x)); return MS((core.length ? core : t).join(' ').replace(/^台(?=[北中南東灣])/, '臺')); };   // 正字統一「臺」(官方名);只動台北/中/南/東/灣開頭,不動煙台等中國地名

  /* ---- catalog-driven poster + zh-name resolution (mirrors js/u.js) ---- */
  let POSTER_BY_TITLE = {};   // title(lower) -> poster url
  let PRODUCTION_BY_KEY = {}; // production_key -> {poster,…}
  let ZH_BY_TITLE = {};       // en title(lower) -> zh name
  let TAG_BY_TITLE = {};      // title(lower) -> 劇種傳統 tag(劇迷類型的劇種軸)
  function posterFor(t) { return POSTER_BY_TITLE[(t || '').toLowerCase()] || null; }
  // 自訂海報常是原始大圖 → 走免費即時縮圖代理 wsrv.nl(寬600+webp)加速；catalog 官方圖不動。
  function proxyImg(u) { if (!u || !/^https?:\/\//i.test(u) || /(wsrv\.nl|weserv\.nl)/i.test(u)) return u;
    if (/[?&]w=\d/i.test(u) || /\bi\d?\.wp\.com\b/i.test(u)) return u;   // 已是縮圖 CDN/含寬度參數 → 不代理
    if (/^https?:\/\/(my\.|www\.)?themusicalmap\.com\//i.test(u)) return u;   // 自家站海報不代理:wsrv webp 把純黑抬成灰(2026-07-15 實測)
    return 'https://wsrv.nl/?url=' + encodeURIComponent(u) + '&w=600&output=webp&q=82'; }
  function resolvePoster(s) {
    if (s.poster_override && safeUrl(s.poster_override)) return proxyImg(s.poster_override);
    const p = s.production_key && PRODUCTION_BY_KEY[s.production_key];
    if (p && p.poster) return p.poster;
    return posterFor(s.title);
  }
  // 自訂海報的「備援官方海報」:外站圖床會死(2026-07-10 實案:IG 簽章 URL 過期,
  // Phantom 卡整張退成文字卡)。死了退 catalog/production 官方圖,體驗不歸零。
  function altPoster(s) {
    if (!s.poster_override) return null;   // 沒自訂=本來就用官方圖,無備援需求
    const p = s.production_key && PRODUCTION_BY_KEY[s.production_key];
    return (p && p.poster) || posterFor(s.title) || null;
  }
  function buildCatalogMaps(cat) {
    Object.values(cat.productions || {}).forEach((arr) => arr.forEach((p) => { PRODUCTION_BY_KEY[p.key] = p; }));
    (cat.titles || []).forEach((t) => {
      const p = cat.posters ? cat.posters[t.group] : null;
      if (t.en) { const k = t.en.toLowerCase(); if (p) POSTER_BY_TITLE[k] = p; if (t.zh) ZH_BY_TITLE[k] = t.zh; if (t.tag) TAG_BY_TITLE[k] = t.tag; }
      if (t.zh) { const kz = t.zh.toLowerCase(); if (p) POSTER_BY_TITLE[kz] = p; if (t.tag) TAG_BY_TITLE[kz] = t.tag; }
    });
  }

  /* upgrade a stored sighting's venue name to the catalog's current name (by coord) */
  function distM(a, b, c, d) {
    const R = 6371008.8, p = Math.PI / 180;
    const h = 0.5 - Math.cos((c - a) * p) / 2 + Math.cos(a * p) * Math.cos(c * p) * (1 - Math.cos((d - b) * p)) / 2;
    return 2 * R * Math.asin(Math.sqrt(h));
  }
  function upgradeVenueNames(rows, cat) {
    const cv = (cat.venues || []).filter((v) => typeof v.lat === 'number');
    const current = new Set(cv.map((v) => v.name));
    rows.forEach((s) => {
      if (!s.venue || typeof s.lat !== 'number') return;
      if (current.has(s.venue)) return;
      const near = cv.filter((v) => distM(s.lat, s.lng, v.lat, v.lng) <= 40);
      if (near.length === 1) s.venue = near[0].name;
    });
    // en 模式:純 CJK 館名回 catalog 查官方英文名(與 me.html venueEnOf 同邏輯;查不到保留原文)
    if (EN_UI) {
      const vens = cat.venues || [];
      rows.forEach((s) => {
        if (!s.venue) return;
        const parts = String(s.venue).split(/\s+/);
        const latin = parts.filter((x) => !_cjk.test(x)).join(' ').trim();
        if (latin) return;   // 已含英文部分,交給 venueZh 抽取
        const zh = parts.filter((x) => _cjk.test(x)).join(' ').trim();
        const hit = vens.find((c) => c.search && c.search.includes(zh)) || vens.find((c) => c.name && c.name.includes(zh));
        if (hit) { const en = String(hit.name).split(/\s+/).filter((x) => !_cjk.test(x)).join(' ').trim(); if (en) s.venue = hit.name; }
      });
    }
  }

  /* RPC seen_date (full) + precision → the partial date string me.html expects */
  function precisionOf(seen) { if (!seen) return 'none'; const d = String(seen); return d.length === 4 ? 'year' : d.length === 7 ? 'month' : 'day'; }
  function partialDate(seen, prec) { if (!seen) return ''; const p = prec || precisionOf(seen); if (p === 'year') return seen.slice(0, 4); if (p === 'month') return seen.slice(0, 7); return seen; }

  /* ---- empty / not-found ---- */
  function showEmpty(mode) {
    const w = document.getElementById('pub-wrap'); if (w) w.style.display = 'none';
    const e = document.getElementById('pub-empty'); if (e) e.hidden = false;
    // 'none'=帳號存在且公開但 0 筆(≠不存在):換成「還沒有紀錄」文案,別誤導成頁面不存在(2026-07-10)
    if (mode === 'none') {
      const ti = document.querySelector('#pub-empty [data-i18n="empty_title"]');
      const su = document.querySelector('#pub-empty [data-i18n="empty_sub"]');
      if (ti) { ti.setAttribute('data-i18n', 'empty_none_title'); ti.textContent = T('empty_none_title'); }
      if (su) { su.setAttribute('data-i18n', 'empty_none_sub'); su.textContent = T('empty_none_sub'); }
    }
  }

  /* ============================================================================
     RENDER — ported verbatim from me.html (owner view). Runs once, after MM.shows
     has been populated from the public profile. Read-only: no edit/delete/add.
     ========================================================================== */
  function render() {
    const S = MM.shows, st = MM.stats('past'), stAll = MM.stats();   // st=只算已看過；stAll=含未來（年份 chips）
    const isFut = d => MM.isFuture(d);
    const upd = d => String(d || '').replace(/-/g, ' / ');   // 未來卡日期 "2026 / 11 / 09"
    const FLAG = {};   // 不顯示國旗 emoji
    const MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    const fdt = d => { if (!d) return T('date_tbd'); const [y, m, dd] = d.split('-');
      if (dd) return `${MON[+m - 1]} ${+dd}, ${y}`;
      if (m) return `${MON[+m - 1]} ${y}`;
      return `${y}`; };
    const fshort = d => { if (!d) return ''; const [y, m] = d.split('-'); return m ? `${y}.${m}` : `${y}`; };
    const stars = r => '★'.repeat(Math.floor(r)) + (r % 1 >= .5 ? '½' : '');
    function shade(hex, a) { let c = hex.replace('#', ''); let r = parseInt(c.slice(0, 2), 16) + a, g = parseInt(c.slice(2, 4), 16) + a, b = parseInt(c.slice(4, 6), 16) + a; const cl = x => Math.max(0, Math.min(255, x)); return `rgb(${cl(r)},${cl(g)},${cl(b)})`; }
    const venueCode = v => v.replace(/Theatre|Theater|劇場|劇院|\(.*\)/g, '').trim().slice(0, 9).toUpperCase();

    /* hero spines + nums + newest */
    (function () {
      const sp = document.getElementById('spines');
      [...S, ...S].slice(0, 16).forEach(s => { const i = document.createElement('i'); i.style.background = `linear-gradient(160deg,${shade(s.color, 28)},${shade(s.color, -50)})`; sp.appendChild(i); });
      const bn = document.getElementById('bignums');
      [['<b>' + st.total + '</b>', T('bn_musicals')], [st.unique, T('bn_unique')], [st.cities, T('bn_cities')], [st.countries, T('bn_countries')]]
        .forEach(([n, l]) => { const d = document.createElement('div'); d.className = 'bn'; d.innerHTML = `<div class="n tnum">${n}</div><div class="l">${l}</div>`; bn.appendChild(d); });
      const newest = MM.recent(true)[0];   // 只取已發生的最近一場
      const up = stAll.upcoming || 0;
      const upTxt = up > 0 ? ` <span class="nw" style="color:var(--gold)">${esc(TN('upcoming_dot_n', { n: up }))}</span>` : '';
      document.getElementById('newest').innerHTML = newest
        ? `<span class="dot"></span><span class="nw">${esc(T('newest_label'))} <b>${esc(newest.title)}</b></span> <span class="nw">${esc(newest.city)}${newest.date ? ' · ' + fshort(newest.date) : ''}</span>${upTxt}`
        : (up > 0 ? `<span class="dot"></span><span class="nw">${esc(T('none_yet'))}</span><span class="nw" style="color:var(--gold)">${esc(TN('upcoming_n', { n: up }))}</span>` : '');
    })();

    /* ---------- POSTER WALL ---------- */
    let activeYear = '全部', activeCity = null, sortBy = 'date';
    function filtered() {
      let a = S.filter(s => (activeYear === '全部' || s.date.startsWith(activeYear)) && (!activeCity || s.city === activeCity));
      if (sortBy === 'date') a.sort((x, y) => y.date.localeCompare(x.date));
      if (sortBy === 'rating') a.sort((x, y) => y.rating - x.rating || y.date.localeCompare(x.date));
      if (sortBy === 'count') { const cnt = {}; a.forEach(s => { cnt[s.title] = (cnt[s.title] || 0) + 1; });
        a.sort((x, y) => (cnt[y.title] - cnt[x.title]) || x.title.localeCompare(y.title) || (y.date || '').localeCompare(x.date || '')); }
      if (sortBy === 'title') a.sort((x, y) => x.title.localeCompare(y.title));
      return a;
    }
    function posterEl(s) {
      const c = document.createElement('button'); c.className = 'card'; c.style.setProperty('--accent', s.color);
      const fut = isFut(s.date); if (fut) c.classList.add('is-future');
      c.innerHTML = `<figure class="poster" style="margin:0${s.posterBg ? ';background:' + s.posterBg : ''}">
          <div class="skel"></div>
          <img alt="${esc(s.title)} poster" loading="lazy" decoding="async" referrerpolicy="no-referrer" ${s.posterFit === 'contain' ? 'style="object-fit:contain;object-position:center"' : ''}/>
          <figcaption class="fallback"><span class="kick">A Musical</span><span class="ft">${esc(s.title)}</span><span class="fzh">${esc(s.zh)}</span><span class="rule"></span></figcaption>
          <div class="topfx"></div>
          ${fut ? `<div class="up-veil"></div><div class="up-ribbon">${esc(T('ribbon_upcoming'))}</div>` : ''}
          <span class="flag">${FLAG[s.country] || ''}</span>${s.fav ? '<span class="fav">♥</span>' : ''}
        </figure>
        <div class="cap"><span class="cap-t"><span class="en">${esc(s.title)}</span><span class="zh">${esc(s.zh)}</span></span>
          <div class="cap-venue">${esc(venueZh(s.venue) || '')}</div>
          <div class="cap-where">${esc(cityCountry(s))}</div>
          <div class="cap-date">${esc(s.date ? s.date.replace(/-/g, '/') : '')}</div></div>`;
      const img = c.querySelector('img'), fig = c.querySelector('.poster'), skel = c.querySelector('.skel');
      let _retried = false;
      const _fall = () => { if (!_retried && s.posterFull && s.posterFull !== s.poster) { _retried = true; img.src = s.posterFull; return; }
        if (s.posterAlt && img.src !== s.posterAlt) { img.src = s.posterAlt; return; }   // 自訂圖床死→退官方海報(alt 也死時 src 已相等,自然落到色塊,不迴圈)
        fig.classList.add('is-fallback'); };   // 代理失敗→原圖→官方備援→都失敗才色塊
      // wsrv 代理對擋外部代理的圖床會等 upstream 逾時才回 503——4s 沒載入就搶先走備援(2026-07-14 me 頁同修)
      const _t = (s.poster && s.posterFull && s.posterFull !== s.poster) ? setTimeout(() => { if (!img.complete || !img.naturalWidth) _fall(); }, 4000) : null;
      img.onload = () => { if (_t) clearTimeout(_t); img.classList.add('ready'); skel.style.display = 'none';
        // 比例智慧切換(與 me.html 同步 2026-07-15):偏離 2:3 逾 8% → contain+黑底
        if (s.posterFit !== 'contain' && img.naturalWidth && img.naturalHeight) {
          const dev = Math.abs(img.naturalWidth / img.naturalHeight - 2 / 3) / (2 / 3);
          if (dev > 0.08) { img.style.objectFit = 'contain'; img.style.objectPosition = 'center'; fig.style.background = '#0c0b10'; }
        } };
      img.onerror = () => { if (_t) clearTimeout(_t); _fall(); };
      img.src = s.poster || '';
      if (!s.poster) fig.classList.add('is-fallback');
      c.onclick = () => openDetail(s);
      return c;
    }
    function renderPoster() {
      const w = document.getElementById('wall-poster'); w.innerHTML = '';
      const list = filtered();
      list.forEach((s, i) => { const el = posterEl(s); el.classList.add('reveal'); el.style.setProperty('--i', i % 12); w.appendChild(el); io.observe(el); });
      document.getElementById('count').textContent = TN('n_musicals', { n: list.length });
    }
    /* ---------- LOG LIST VIEW ---------- */
    function renderLog() {
      const el = document.getElementById('wall-log'); const list = filtered();
      document.getElementById('count').textContent = TN('n_musicals', { n: list.length });
      el.innerHTML = `<div class="logtable" role="table">
        <div class="lt-head" role="row"><span>${esc(T('lt_show'))}</span><span>${esc(T('lt_city'))}</span><span>${esc(T('lt_date'))}</span><span>${esc(T('lt_rate'))}</span></div>` +
        list.map(s => `<button class="lt-row" data-id="${s.id}" role="row">
          <span class="lt-show"><span class="lt-thumb">${s.poster ? `<img src="${esc(s.poster)}" loading="lazy" decoding="async" referrerpolicy="no-referrer" alt=""/>` : `<i>${esc((s.title || '?').trim()[0] || '?')}</i>`}</span>
            <span class="lt-t"><b>${esc(s.title)}</b>${s.zh ? `<i>${esc(s.zh)}</i>` : ''}</span></span>
          <span class="lt-city">${s.city ? esc(cityName(s.city)) : '<span class="muted">—</span>'} ${s.country ? (FLAG[s.country] || '') : ''}</span>
          <span class="lt-date">${fshort(s.date) || `<span class="muted">${esc(T('lt_tbd'))}</span>`}</span>
          <span class="lt-rate">${s.rating ? '★'.repeat(s.rating) : '<span class="muted">—</span>'}</span>
        </button>`).join('') + `</div>`;
      el.querySelectorAll('.lt-row').forEach(r => r.onclick = () => { const sh = S.find(x => String(x.id) === r.dataset.id); if (sh) openDetail(sh); });
    }

    /* ---------- PASSPORT FACE ---------- */
    function stampSvg(s) {
      const id = 'p' + s.id, rot = ((s.id * 37) % 9) - 4;
      const top = `M 16 64 A 48 48 0 0 1 112 64`, bot = `M 18 64 A 46 46 0 0 0 110 64`;
      const _y = s.date ? s.date.slice(0, 4) : '', _m = (s.date && s.date.length >= 7) ? +s.date.slice(5, 7) : 0, _d = (s.date && s.date.length >= 10) ? s.date.slice(8, 10) : '';
      const dd = _d ? `${_d}·${MON[_m - 1].toUpperCase()}·${_y}` : (_m ? `${MON[_m - 1].toUpperCase()}·${_y}` : (_y || '—'));
      const enTitle = (s.title.length > 15 ? venueShort(s.title) : s.title).toUpperCase();
      // 城市名截斷:圓形戳章底弧空間有限,長名(SÃO PAULO、中文長名)會溢出弧線(2026-07-10);null 防呆
      // ≤16 字完整(SAN FRANCISCO 不再切成 SAN FRANCISC);需截斷才在詞界斷(2026-07-10)
      const _sc = String(s.city || '—').toUpperCase();
      const stampCity = _sc.length <= 16 ? _sc : (() => { const c = _sc.slice(0, 16), sp = c.lastIndexOf(' '); return sp > 8 ? c.slice(0, sp) : c; })();
      return `<svg viewBox="0 0 128 128" style="--rot:${rot}deg">
        <defs><path id="${id}t" d="${top}"/><path id="${id}b" d="${bot}"/></defs>
        <circle cx="64" cy="64" r="56" fill="none" stroke="currentColor" stroke-width="2.4"/>
        <circle cx="64" cy="64" r="48" fill="none" stroke="currentColor" stroke-width="1"/>
        <text font-size="10.5" letter-spacing="1.2" fill="currentColor" font-family="Inter,sans-serif" font-weight="700">
          <textPath href="#${id}t" startOffset="50%" text-anchor="middle">${esc(enTitle)}</textPath></text>
        <text font-size="8" letter-spacing="1" fill="currentColor" font-family="Inter,sans-serif">
          <textPath href="#${id}b" startOffset="50%" text-anchor="middle">${esc(stampCity)} · ${esc(venueCode(s.venue))}</textPath></text>
        <g transform="rotate(1.5 64 64)"><text x="64" y="68" font-size="12" text-anchor="middle" font-family="'IBM Plex Mono',monospace" font-weight="600" fill="currentColor">${dd}</text></g>
      </svg>`;
    }
    function venueShort(t) { const m = { 'The Phantom of the Opera': 'PHANTOM', 'Les Misérables': 'LES MIS', "Standing at the Sky's Edge": "SKY'S EDGE", 'The Book of Mormon': 'BOOK OF MORMON', 'König der Löwen': 'LÖWEN' }; return m[t] || t.slice(0, 14); }
    function milestoneFor(s, idxInCountry, firstOfCountry) {
      if (firstOfCountry) return s.country === 'United Kingdom' ? 'FIRST WEST END' : s.country === 'United States' ? 'FIRST BROADWAY' : 'FIRST';
      return null;
    }
    function renderPassport() {
      const w = document.getElementById('wall-passport'); w.innerHTML = '';
      const list = filtered();
      document.getElementById('count').textContent = TN('n_musicals', { n: list.length });
      const byC = {}; list.forEach(s => { (byC[s.country] = byC[s.country] || []).push(s); });
      const order = Object.keys(byC).sort((a, b) => byC[b].length - byC[a].length);
      order.forEach(co => {
        const arr = byC[co].sort((a, b) => a.date.localeCompare(b.date));
        const cities = [...new Set(arr.map(s => s.city))].join(' · ');
        const stamped = arr.filter(s => !isFut(s.date)).length;   // 只算已到場的戳章數
        const v = document.createElement('div'); v.className = 'visa reveal';
        v.innerHTML = `<div class="crow"><span class="cn">${esc(countryZh(co) || '—')}</span>
          <span class="ct">${esc(cities)}</span><span class="prog">${stamped} STAMP${stamped !== 1 ? 'S' : ''}</span></div>
          <div class="stamps">${arr.map((s, j) => {
            const dly = Math.min(j * 0.05, 0.5).toFixed(2); const mile = milestoneFor(s, j, j === 0); const fut = isFut(s.date);
            return `<div class="stamp${fut ? ' is-future' : ''}" data-sid="${s.id}" role="button" tabindex="0" aria-label="${esc((s.title || '') + (fut ? T('up_suffix') : '') + T('detail_suffix'))}" style="--ink:${esc(s.color)};--rot:${(((s.id * 37) % 9) - 4)}deg;--dly:${dly}s">
              ${mile && !fut ? `<span class="mile">${mile}</span>` : ''}${stampSvg(s)}${fut ? `<span class="up-mark">${T('up_mark')}</span>` : ''}</div>`; }).join('')}</div>`;
        w.appendChild(v); io.observe(v);
      });
      w.querySelectorAll('.stamp[data-sid]').forEach(el => { const open = () => { const sh = S.find(x => String(x.id) === el.dataset.sid); if (sh) openDetail(sh); };
        el.onclick = open; el.onkeydown = e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); open(); } }; });
      stampIo.disconnect();
      w.querySelectorAll('.visa').forEach(vp => stampIo.observe(vp));
    }
    const stampIo = new IntersectionObserver(es => { es.forEach(e => { if (e.isIntersecting) { e.target.querySelectorAll('.stamp').forEach(s => s.classList.add('in')); stampIo.unobserve(e.target); } }); }, { threshold: .12 });

    /* ---------- mode toggle (View Transitions) ---------- */
    let mode = 'poster';
    function setMode(m) {
      if (m === mode) return; mode = m;
      const doSwap = () => {
        const pw = document.getElementById('wall-poster'), pp = document.getElementById('wall-passport'), pl = document.getElementById('wall-log');
        document.querySelectorAll('#seg button').forEach(b => b.setAttribute('aria-pressed', b.dataset.mode === m));
        moveThumb();
        pw.classList.toggle('off', m !== 'poster'); pp.classList.toggle('on', m === 'passport'); pl.classList.toggle('on', m === 'log');
        if (m === 'poster') renderPoster(); else if (m === 'passport') renderPassport(); else renderLog();
      };
      if (document.startViewTransition) document.startViewTransition(doSwap); else doSwap();
    }
    function moveThumb() { const seg = document.getElementById('seg'), thumb = document.getElementById('segthumb');
      const btn = seg.querySelector(`[data-mode="${mode}"]`); thumb.style.width = btn.offsetWidth + 'px'; thumb.style.transform = `translateX(${btn.offsetLeft - 4}px)`; }
    document.getElementById('seg').addEventListener('click', e => { const b = e.target.closest('button'); if (b) setMode(b.dataset.mode); });

    /* chips */
    (function () { const c = document.getElementById('chips');
      // filter(Boolean):未填日期的紀錄 yr()='' 會混進 years → 空白 chip(同 me.html 修法)
      ['全部', ...stAll.years.filter(Boolean)].forEach((y, i) => { const b = document.createElement('button'); b.className = 'chip'; b.textContent = (y === '全部' ? T('chip_all') : y); b.setAttribute('aria-pressed', i === 0);
        b.onclick = () => { activeYear = y; activeCity = null; [...c.children].forEach(x => x.setAttribute('aria-pressed', 'false')); b.setAttribute('aria-pressed', 'true'); rerender(); }; c.appendChild(b); }); })();
    document.getElementById('sort').onchange = e => { sortBy = e.target.value; rerender(); };
    function rerender() { mode === 'poster' ? renderPoster() : mode === 'passport' ? renderPassport() : renderLog(); }

    /* scroll reveal */
    const io = new IntersectionObserver(es => { es.forEach(e => { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } }); }, { rootMargin: '0px 0px -8% 0px', threshold: .08 });
    document.querySelectorAll('.reveal').forEach(el => io.observe(el));

    /* ---------- MAP ---------- */
    const CITYZH = {"Aarhus": "奧胡斯", "Adelaide": "阿得雷德", "Aichi": "愛知", "Albuquerque": "阿布奎基", "Amsterdam": "阿姆斯特丹", "Ann Arbor": "安娜堡", "Antwerp": "安特衛普", "Atlanta": "亞特蘭大", "Auckland": "奧克蘭", "Austin": "奧斯汀", "Baltimore": "巴爾的摩", "Barcelona": "巴塞隆納", "Beijing": "北京", "Belfast": "貝爾法斯特", "Berlin": "柏林", "Birmingham": "伯明罕", "Boston": "波士頓", "Brighton": "布萊頓", "Brisbane": "布里斯本", "Bristol": "布里斯托", "Brussels": "布魯塞爾", "Budapest": "布達佩斯", "Buenos Aires": "布宜諾斯艾利斯", "Buffalo": "水牛城", "Busan": "釜山", "Calgary": "卡加利", "Cambridge": "劍橋", "Canberra": "坎培拉", "Canterbury": "坎特伯里", "Cardiff": "卡地夫", "Changsha": "長沙", "Changzhou": "常州", "Charlotte": "夏洛特", "Chengdu": "成都", "Chiayi": "嘉義", "Chicago": "芝加哥", "Chongqing": "重慶", "Cincinnati": "辛辛那提", "Cleveland": "克里夫蘭", "Cologne": "科隆", "Columbus": "哥倫布", "Copenhagen": "哥本哈根", "Daegu": "大邱", "Dalian": "大連", "Dallas": "達拉斯", "Daqing": "大慶", "Denver": "丹佛", "Detroit": "底特律", "Dezhou": "德州", "Dongguan": "東莞", "Dubai": "杜拜", "Dublin": "都柏林", "Edinburgh": "愛丁堡", "Edmonton": "愛德蒙頓", "Firenze": "佛羅倫斯", "Fort Lauderdale": "羅德岱堡", "Fort Worth": "沃斯堡", "Foshan": "佛山", "Frankfurt": "法蘭克福", "Fukuoka": "福岡", "Fuzhou": "福州", "Ganzhou": "贛州", "Ghent": "根特", "Gifu": "岐阜", "Glasgow": "格拉斯哥", "Gothenburg": "哥德堡", "Grand Rapids": "大急流城", "Guangzhou": "廣州", "Guilin": "桂林", "Göteborg": "哥德堡", "Haikou": "海口", "Hamburg": "漢堡", "Hangzhou": "杭州", "Harbin": "哈爾濱", "Hefei": "合肥", "Helsinki": "赫爾辛基", "Hengyang": "衡陽", "Hiroshima": "廣島", "Houston": "休士頓", "Hsinchu": "新竹", "Huai'an": "淮安", "Hyogo": "兵庫", "Jiaxing": "嘉興", "Jinan": "濟南", "Kanagawa": "神奈川", "Kansas City": "堪薩斯城", "Kaohsiung": "高雄", "Kunshan": "崑山", "Köln": "科隆", "København": "哥本哈根", "København V": "哥本哈根", "Langfang": "廊坊", "Las Vegas": "拉斯維加斯", "Leeds": "里茲", "Lishui": "麗水", "Liverpool": "利物浦", "London": "倫敦", "Los Angeles": "洛杉磯", "Louisville": "路易斯維爾", "Lyon": "里昂", "Madison": "麥迪遜", "Madrid": "馬德里", "Maihama": "舞濱", "Manchester": "曼徹斯特", "Melbourne": "墨爾本", "Memphis": "曼菲斯", "Mexico City": "墨西哥市", "Miami": "邁阿密", "Milano": "米蘭", "Milwaukee": "密爾瓦基", "Minneapolis": "明尼阿波利斯", "Monterrey": "蒙特雷", "Montreal": "蒙特婁", "Munich": "慕尼黑", "México": "墨西哥市", "München": "慕尼黑", "Nagoya": "名古屋", "Nanchang": "南昌", "Nanjing": "南京", "Nanning": "南寧", "Nantong": "南通", "Napoli": "拿坡里", "Nashville": "納許維爾", "New Orleans": "紐奧良", "New Taipei": "新北", "New York": "紐約", "Newcastle": "紐卡索", "Ningbo": "寧波", "Nottingham": "諾丁罕", "Oklahoma City": "奧克拉荷馬市", "Omaha": "奧馬哈", "Orlando": "奧蘭多", "Osaka": "大阪", "Oslo": "奧斯陸", "Ottawa": "渥太華", "Oxford": "牛津", "Padova": "帕多瓦", "Paris": "巴黎", "Penghu": "澎湖", "Perth": "伯斯", "Philadelphia": "費城", "Phoenix": "鳳凰城", "Pingtung": "屏東", "Pittsburgh": "匹茲堡", "Portland": "波特蘭", "Prague": "布拉格", "Praha": "布拉格", "Providence": "普羅維登斯", "Qidong": "啓東", "Qingdao": "青島", "Quanzhou": "泉州", "Quzhou": "衢州", "Reno": "雷諾", "Richmond": "里奇蒙", "Rio de Janeiro": "里約熱內盧", "Roma": "羅馬", "Rotorua": "羅托魯瓦", "Rotterdam": "鹿特丹", "Saint Louis": "聖路易", "Salt Lake City": "鹽湖城", "San Antonio": "聖安東尼奧", "San Diego": "聖地牙哥", "San Francisco": "舊金山", "San Jose": "聖荷西", "Sapporo": "札幌", "Seattle": "西雅圖", "Seoul": "首爾", "Shanghai": "上海", "Shaoxing": "紹興", "Sheffield": "雪菲爾", "Shenyang": "瀋陽", "Shenzhen": "深圳", "Singapore": "新加坡", "Southampton": "南安普頓", "St. Louis": "聖路易", "Stockholm": "斯德哥爾摩", "Stuttgart": "斯圖加特", "Suzhou": "蘇州", "Swansea": "斯旺西", "Sydney": "雪梨", "São Paulo": "聖保羅", "Taichung": "臺中", "Taipei": "臺北", "Taitung": "臺東", "Taiyuan": "太原", "Taizhou": "台州", "Takarazuka (兵庫)": "寶塚", "Tampa": "坦帕", "Tianjin": "天津", "Tokyo": "東京", "Tokyo (日比谷)": "東京", "Torino": "杜林", "Toronto": "多倫多", "Tucson": "土桑", "Utrecht": "烏特勒支", "Vancouver": "溫哥華", "Victoria": "維多利亞", "Vienna": "維也納", "Warsaw": "華沙", "Warszawa": "華沙", "Washington": "華盛頓", "Weifang": "濰坊", "Wellington": "威靈頓", "Wenzhou": "溫州", "West Palm Beach": "西棕櫚灘", "Wien": "維也納", "Wimbledon": "溫布頓", "Wuhan": "武漢", "Wuxi": "無錫", "Xi'an": "西安", "Xiamen": "廈門", "Xining": "西寧", "Xuzhou": "徐州", "Yantai": "煙台", "Yinchuan": "銀川", "Yokohama": "橫濱", "York": "約克", "Yunlin": "雲林", "Zhengzhou": "鄭州", "Zhongshan": "中山", "Zhuhai": "珠海", "Zhuji": "諸暨", "Zibo": "淄博", "Zurich": "蘇黎世", "Zürich": "蘇黎世", "连云港": "連雲港"};
    function cityName(c) { if (EN_UI || !c) return c || ''; const base = String(c).replace(/,\s*[A-Za-z.]{2,}$/, '').trim(); return MS(CITYZH[c] || CITYZH[base] || c); }
    function cityHasZh(c) { return cityName(c) !== c; }
    // 城邦 city===country(翻譯後)只顯示一次,避免「新加坡 · 新加坡」
    function cityCountry(s, sep) { const cw = cityName(s.city), co = countryZh(s.country); sep = sep || ' · '; return (co && co !== cw) ? [cw, co].filter(Boolean).join(sep) : (cw || co || ''); }
    function project(lat, lng) { return [(lng + 180) / 360, (90 - lat) / 180]; }
    let mapV = { z: 1, x: 0, y: 0 };
    function clampV() { if (mapV.z < 1) mapV.z = 1; const m = 1 - 1 / mapV.z; mapV.x = Math.max(0, Math.min(m, mapV.x)); mapV.y = Math.max(0, Math.min(m, mapV.y)); if (mapV.z <= 1) { mapV.x = 0; mapV.y = 0; } }
    function tf(fx, fy) { return [(fx - mapV.x) * mapV.z, (fy - mapV.y) * mapV.z]; }
    function renderMap() { drawMap(); positionPins(); }
    function filterToCity(city) { activeCity = activeCity === city ? null : city; activeYear = '全部';
      document.querySelectorAll('#chips .chip').forEach((x, i) => x.setAttribute('aria-pressed', i === 0 && !activeCity));
      if (mode !== 'poster') setMode('poster'); else renderPoster();
      document.getElementById('wall-poster').scrollIntoView({ behavior: 'smooth', block: 'start' }); }
    function drawMap() {
      const cv = document.getElementById('mapcv'); const wrap = cv.parentElement;
      const w = wrap.clientWidth, h = wrap.clientHeight, dpr = Math.min(2, window.devicePixelRatio || 1);
      if (!w || !h) return;
      cv.width = w * dpr; cv.height = h * dpr; const ctx = cv.getContext('2d'); ctx.scale(dpr, dpr); ctx.clearRect(0, 0, w, h);
      const cs = getComputedStyle(document.documentElement);
      const fill = cs.getPropertyValue('--land-fill').trim() || '#1b2747';
      const dot = cs.getPropertyValue('--land-dot').trim() || 'rgba(132,151,184,.85)';
      const pts = WORLD_DOTS.split(' ');
      const k = Math.min(2.4, 0.72 + mapV.z * 0.16);
      ctx.globalAlpha = .6; ctx.fillStyle = fill;
      for (const p of pts) { const i = p.indexOf(','); const [sx, sy] = tf(+p.slice(0, i) / 1000, +p.slice(i + 1) / 500);
        if (sx < -.03 || sx > 1.03 || sy < -.03 || sy > 1.03) continue; ctx.beginPath(); ctx.arc(sx * w, sy * h, 3.1 * k, 0, 7); ctx.fill(); }
      ctx.globalAlpha = 1; ctx.fillStyle = dot;
      for (const p of pts) { const i = p.indexOf(','); const [sx, sy] = tf(+p.slice(0, i) / 1000, +p.slice(i + 1) / 500);
        if (sx < -.03 || sx > 1.03 || sy < -.03 || sy > 1.03) continue; ctx.beginPath(); ctx.arc(sx * w, sy * h, 1.5 * k, 0, 7); ctx.fill(); }
    }
    let PINS = [];
    function placePins() {
      const pins = document.getElementById('pins'); pins.innerHTML = ''; PINS = [];
      const byCity = {}; S.forEach(s => { if (!s.city || isFut(s.date)) return; (byCity[s.city] = byCity[s.city] || { ...s, n: 0 }).n++; });   // 地圖/城市榜只算已到場
      Object.values(byCity).forEach(c => {
        if (c.lat == null || c.lng == null) return;
        const [px, py] = project(c.lat, c.lng); if (!isFinite(px) || !isFinite(py)) return;
        const sz = 15 + Math.sqrt(c.n) * 6.5;
        const el = document.createElement('button'); el.className = 'pin';
        el.setAttribute('aria-label', TN('pin_aria', { city: c.city, n: c.n }));
        el.innerHTML = `<span class="glow" style="width:${sz * 2.4}px;height:${sz * 2.4}px"></span>
          <span class="ring"></span>
          <span class="core" style="width:${sz}px;height:${sz}px">${c.n}</span>
          <span class="lbl">${esc(cityName(c.city))}</span>`;
        el.onclick = () => filterToCity(c.city);
        pins.appendChild(el); PINS.push({ el, px, py, n: c.n });
      });
      positionPins();
    }
    // 重疊城市併成 cluster(圈圈=總場次+「N 城市」,點擊放大展開)——與 me.html 同步移植;
    // 公開分享頁沒做會讓訪客看到擠成一團的 marker(姊妹頁同 bug)。CSS 共用 me-v2.css 的 .pin-cluster。
    let CLUSTER_POOL = [];
    function positionPins() {
      const host = document.getElementById('pins'); if (!host) return;
      const W = host.clientWidth || 600, H = host.clientHeight || 375;
      const vis = [];
      PINS.forEach(p => { const [sx, sy] = tf(p.px, p.py);
        if (sx < -0.02 || sx > 1.02 || sy < -0.02 || sy > 1.02) { p.el.style.display = 'none'; }
        else { p._sx = sx; p._sy = sy; vis.push(p); } });
      vis.sort((a, b) => b.n - a.n);                       // 場次多者當 cluster 錨點
      // R 隨 zoom 縮小;zoom 封頂(12)時不再併群(R=0),否則相近城市(台北/台中 ~22px)點到 max zoom 也永不展開=死胡同
      const R = mapV.z >= 11.5 ? 0 : (mapV.z >= 6 ? 22 : 44), used = new Set(), clusters = [];
      vis.forEach(a => { if (used.has(a)) return; used.add(a); const mem = [a];
        vis.forEach(b => { if (used.has(b)) return; const dx = (a._sx - b._sx) * W, dy = (a._sy - b._sy) * H;
          if (dx * dx + dy * dy < R * R) { used.add(b); mem.push(b); } });
        clusters.push(mem); });
      CLUSTER_POOL.forEach(e => e.style.display = 'none');
      const singles = []; let ci = 0;
      clusters.forEach(mem => {
        if (mem.length === 1) { const p = mem[0]; p.el.style.display = ''; p.el.classList.remove('lbl-off');
          p.el.style.left = p._sx * 100 + '%'; p.el.style.top = p._sy * 100 + '%'; singles.push(p); return; }
        mem.forEach(p => p.el.style.display = 'none');
        let cx = 0, cy = 0, bx = 0, by = 0, sum = 0; mem.forEach(p => { cx += p._sx; cy += p._sy; bx += p.px; by += p.py; sum += p.n; });
        const k = mem.length; cx /= k; cy /= k; bx /= k; by /= k;
        let el = CLUSTER_POOL[ci];
        if (!el || !el.isConnected) { el = document.createElement('button'); el.className = 'pin pin-cluster'; host.appendChild(el); CLUSTER_POOL[ci] = el; }   // placePins 清空 #pins 會卸離 cluster 元素→重用前檢查 isConnected
        el.style.display = ''; el.style.left = cx * 100 + '%'; el.style.top = cy * 100 + '%';
        const sz = 18 + Math.sqrt(sum) * 5.2, word = document.documentElement.lang === 'en' ? (k + ' cities') : (k + ' 城市');
        el.innerHTML = `<span class="glow" style="width:${sz * 2.2}px;height:${sz * 2.2}px"></span><span class="core" style="width:${sz}px;height:${sz}px">${sum}</span><span class="lbl">${word}</span>`;
        el.setAttribute('aria-label', document.documentElement.lang === 'en' ? (word + ', ' + sum + ' shows, click to zoom in') : (word + '，共 ' + sum + ' 場，點擊放大'));   // en 模式別唸中文(螢幕閱讀器)
        el.onclick = () => { const nz = Math.min(12, Math.max(mapV.z * 2.4, 2.6)); mapV.z = nz; mapV.x = bx - 0.5 / nz; mapV.y = by - 0.5 / nz; clampV(); renderMap(); };
        ci++;
      });
      try { declutterSingleLabels(singles, host); } catch (e) {}
    }
    function declutterSingleLabels(singles, host) {
      singles.sort((a, b) => b.n - a.n);
      const base = host.getBoundingClientRect(), kept = [];
      singles.forEach(p => { const lbl = p.el.querySelector('.lbl'); if (!lbl) return;
        const r = lbl.getBoundingClientRect(); const box = { x: r.left - base.left, y: r.top - base.top, w: r.width, h: r.height };
        const hit = kept.some(b => box.x < b.x + b.w + 2 && box.x + box.w + 2 > b.x && box.y < b.y + b.h + 2 && box.y + box.h + 2 > b.y);
        if (hit) p.el.classList.add('lbl-off'); else kept.push(box); });
    }
    function buildCityList() {
      const el = document.getElementById('citylist');
      const byCity = {}; S.forEach(s => { if (!s.city || isFut(s.date)) return; (byCity[s.city] = byCity[s.city] || { ...s, n: 0 }).n++; });   // 地圖/城市榜只算已到場
      const arr = Object.values(byCity).sort((a, b) => b.n - a.n);
      el.innerHTML = `<div class="cl-head"><h4>${esc(T('citylist_title'))}</h4><div class="sh">${esc(TN('citylist_sub', { c: arr.length, k: st.countries, t: st.total }))}</div></div>` +
        arr.map(c => { const d = 9 + Math.sqrt(c.n) * 4.2; return `<button class="cl-row" data-city="${esc(c.city)}">
          <span class="d" style="width:${d}px;height:${d}px"></span>
          <span class="nm"><b>${esc(cityName(c.city))}</b><span>${esc(countryZh(c.country))}</span></span>
          <span class="ct">${c.n}</span></button>`; }).join('');
      el.querySelectorAll('.cl-row').forEach(r => r.onclick = () => filterToCity(r.dataset.city));
    }
    let mt; addEventListener('resize', () => { clearTimeout(mt); mt = setTimeout(() => { renderMap(); }, 150); });
    (function () {
      const wrap = document.querySelector('.mapwrap'); if (!wrap) return;
      function zoomAt(cx, cy, factor) { const bx = mapV.x + cx / mapV.z, by = mapV.y + cy / mapV.z;
        mapV.z = Math.max(1, Math.min(12, mapV.z * factor)); mapV.x = bx - cx / mapV.z; mapV.y = by - cy / mapV.z; clampV(); renderMap(); }
      wrap.addEventListener('wheel', e => { e.preventDefault(); const r = wrap.getBoundingClientRect();
        zoomAt((e.clientX - r.left) / r.width, (e.clientY - r.top) / r.height, e.deltaY < 0 ? 1.2 : 1 / 1.2); }, { passive: false });
      let drag = null, _rafP = false;
      const renderMapRAF = () => { if (_rafP) return; _rafP = true; requestAnimationFrame(() => { _rafP = false; renderMap(); }); };  // 合併每 frame 一次(2026-07-10)
      wrap.addEventListener('pointerdown', e => { if (e.target.closest('.pin') || e.target.closest('.mapzoom')) return;
        drag = { x: e.clientX, y: e.clientY }; try { wrap.setPointerCapture(e.pointerId); } catch (_) {} wrap.classList.add('grabbing'); });
      wrap.addEventListener('pointermove', e => { if (!drag) return; const r = wrap.getBoundingClientRect();
        mapV.x -= (e.clientX - drag.x) / (r.width * mapV.z); mapV.y -= (e.clientY - drag.y) / (r.height * mapV.z); drag = { x: e.clientX, y: e.clientY }; clampV(); renderMapRAF(); });
      const end = () => { drag = null; wrap.classList.remove('grabbing'); };
      wrap.addEventListener('pointerup', end); wrap.addEventListener('pointercancel', end); wrap.addEventListener('pointerleave', end);
      const zin = document.getElementById('mapZin'), zout = document.getElementById('mapZout'), zr = document.getElementById('mapZreset');
      if (zin) zin.onclick = () => zoomAt(.5, .5, 1.6);
      if (zout) zout.onclick = () => zoomAt(.5, .5, 1 / 1.6);
      if (zr) zr.onclick = () => { mapV = { z: 1, x: 0, y: 0 }; renderMap(); };
    })();

    /* ---------- badges + toplist + persona ---------- */
    (function () {
      const b = document.getElementById('badges');
      // 徽章=跨過門檻的事件(MM.badges 共用計算),不再把統計數字包成徽章樣式;
      // 公開頁只秀已解鎖(獎盃櫃),未解鎖/0 值一律不渲染。文字無 emoji(2026-07-03 指示)。
      const metal = t => t === 0 ? 'bronze' : t === 1 ? 'silver' : 'gold';
      const bTxt = bd => {
        switch (bd.key) {
          case 'first':     return TN('bd_first', { y: esc(bd.extra) });
          case 'shows':     return TN('bd_shows', { n: bd.reached });
          case 'countries': return TN('bd_countries', { n: bd.reached });
          case 'cities':    return TN('bd_cities', { n: bd.reached });
          case 'works':     return TN('bd_works', { n: bd.reached });
          case 'devotee':   return TN('bd_devotee', { t: esc(bd.extra), n: bd.value });   // 劇名=他人輸入,必跳脫
          case 'double':    return TN('bd_double', { n: bd.value });
          case 'streak':    return TN('bd_streak', { n: bd.value });
        }
        return '';
      };
      const unlocked = MM.badges().filter(x => x.tier >= 0);
      b.innerHTML = unlocked.map(x => `<div class="badge ${metal(x.tier)}">${bTxt(x)}</div>`).join('');
      function barList(id, items, fmt) { const el = document.getElementById(id); if (!el) return;
        if (!items || !items.length) { el.innerHTML = '<div class="sl-empty">—</div>'; return; }
        const mx = items[0][1] || 1;
        el.innerHTML = items.map(([k, v]) => `<div class="sl-row"><span class="sl-k" title="${esc(k)}">${esc(fmt ? fmt(k) : k)}</span><span class="sl-bar"><i style="width:${Math.max(6, v / mx * 100)}%"></i></span><span class="sl-v">${v}</span></div>`).join(''); }   // 全列出+CSS 捲動(與 me.html 同步,2026-07-15)
      barList('sc-shows', st.topShows);
      barList('sc-countries', st.topCountries, countryZh);
      barList('sc-cities', st.topCities, k => `${cityName(k)}`);
      // 劇院榜：以「去廳別的中文館名」重新合併計數（同一劇院不同廳算一間），只算已看過
      { const vc = {}; S.forEach(s => { if (!s.venue || !MM.isPast(s.date)) return; const k = venueZh(s.venue); vc[k] = (vc[k] || 0) + 1; });
        barList('sc-theatres', Object.entries(vc).sort((a, b) => b[1] - a[1])); }
      const _charts = {};
      function lineChart(id, labels, values) {
        const el = document.getElementById(id); if (!el || typeof Chart === 'undefined') return;
        if (_charts[id]) _charts[id].destroy();
        const w = '#ffffff', g = 'rgba(255,255,255,.25)', tc = 'rgba(255,255,255,.9)';
        _charts[id] = new Chart(el, { type: 'line',
          data: { labels, datasets: [{ data: values, borderColor: w, backgroundColor: 'rgba(255,255,255,.22)', fill: true, tension: .3, pointBackgroundColor: w, pointRadius: 3, borderWidth: 2.5 }] },
          options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } },
            scales: { y: { beginAtZero: true, grace: '20%', ticks: { precision: 0, color: tc }, grid: { color: g }, border: { color: g } },
                      x: { ticks: { color: tc }, grid: { color: g }, border: { color: g } } } } });
      }
      const validYears = (st.years || []).filter(y => y && !isNaN(+y)).map(Number);
      let yLabels = [], yVals = [];
      if (validYears.length) { const cnt = {}; (st.perYear || []).forEach(([y, n]) => { if (y && !isNaN(+y)) cnt[+y] = n; });
        const y0 = Math.min(...validYears), y1 = Math.max(...validYears);
        for (let y = y0; y <= y1; y++) { yLabels.push('' + y); yVals.push(cnt[y] || 0); } }
      lineChart('ch-year', yLabels, yVals);
      // 軸標籤在地化(與 me.html 同款修正):中文頁「各月/各星期」不能配 Jan/Sun 英文軸
      const _zhAxis = !EN_UI;
      lineChart('ch-month', (st.perMonth || []).map((x, i) => _zhAxis ? String(i + 1) + '月' : x[0]), (st.perMonth || []).map(x => x[1]));
      lineChart('ch-week', (st.perWeekday || []).map((x, i) => _zhAxis ? MM.WEEKDAYS_ZH[i] : x[0]), (st.perWeekday || []).map(x => x[1]));
      const p = MM.personality();
      document.getElementById('persona').innerHTML = (p.enough === false)
        ? `<h3>${esc(T('persona_title'))}</h3><div class="pb">${esc(p.blurb)}</div>`
        : `<h3>${esc(T('persona_title'))}</h3>
        <div class="pn">${esc(p.nickname)}</div><div class="pb">${esc(p.blurb)}</div>
        <div class="axes">${p.axes.map(a => { const pos = a[2];   // 連續定位(6–94),不再是 14/86 二元假光譜
          return `<div class="axis"><div class="r"><span class="${pos <= 40 ? 'on' : ''}">${esc(a[0])}</span><span>${esc(a[3])}</span><span class="${pos >= 60 ? 'on' : ''}">${esc(a[1])}</span></div><div class="track"><i style="left:calc(${pos}% - 6px)"></i></div></div>`; }).join('')}</div>`;
    })();

    /* ---------- detail modal (read-only) ---------- */
    const dlg = document.getElementById('detail');
    function openDetail(s) {
      const dp = document.getElementById('dt-poster'), img = document.getElementById('dt-img');
      if (s.poster) { dp.classList.remove('is-fallback');
        img.style.objectFit = s.posterFit === 'contain' ? 'contain' : 'cover';
        if (img.getAttribute('src') !== s.poster) {
          img.classList.remove('ready'); let _dtr = false;
          const _dfall = () => { if (!_dtr && s.posterFull && s.posterFull !== s.poster) { _dtr = true; img.src = s.posterFull; return; }
            if (s.posterAlt && img.src !== s.posterAlt) { img.src = s.posterAlt; return; }   // 自訂圖床死→退官方海報
            img.classList.add('ready'); };  // 代理失敗→原圖→官方備援
          const _dt = (s.posterFull && s.posterFull !== s.poster) ? setTimeout(() => { if (!img.complete || !img.naturalWidth) _dfall(); }, 4000) : null;  // 代理 4s 沒回→搶先備援
          img.onload = () => { if (_dt) clearTimeout(_dt); img.classList.add('ready'); };
          img.onerror = () => { if (_dt) clearTimeout(_dt); _dfall(); };
          img.src = s.poster;
        } else img.classList.add('ready'); }
      else { dp.classList.add('is-fallback'); img.removeAttribute('src'); dp.style.setProperty('--dt-accent', s.color || '#7c5cff');
        document.getElementById('dt-fb-en').textContent = s.title; document.getElementById('dt-fb-zh').textContent = s.zh || ''; }
      // 點海報→開原圖;補鍵盤可及(同 me.html)
      const openFull = () => { const full = s.posterFull || s.poster; if (full) window.open(full, '_blank', 'noopener'); };
      dp.onclick = openFull;
      dp.style.cursor = s.poster ? 'zoom-in' : 'default';
      if (s.poster) { dp.tabIndex = 0; dp.setAttribute('role', 'button'); dp.setAttribute('aria-label', T('dt_zoom')); dp.onkeydown = e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); openFull(); } }; }
      else { dp.removeAttribute('tabindex'); dp.removeAttribute('role'); dp.onkeydown = null; }
      document.getElementById('dt-en').textContent = s.title;
      document.getElementById('dt-zh').textContent = s.zh;
      const rt = document.getElementById('dt-rate');
      if (s.rating > 0) { rt.textContent = stars(s.rating) + `  ${s.rating}/5`; rt.style.display = ''; }
      else { rt.textContent = ''; rt.style.display = 'none'; }
      // 唯讀：座位/票價只在有值時顯示（公開頁隱私由 RPC 決定回不回傳）
      const rows = [
        `<dt>${esc(T('dt_venue'))}</dt><dd>${esc(venueZh(s.venue) || '—')}</dd>`,
        `<dt>${esc(T('dt_city'))}</dt><dd>${esc(cityCountry(s, ', ') || '—')} ${FLAG[s.country] || ''}</dd>`,
        `<dt>${esc(T('dt_date'))}</dt><dd>${esc(s.date ? s.date.replace(/-/g, '/') : '—')}</dd>`,
      ];
      if (s.time) rows.push(`<dt>${esc(T('dt_time'))}</dt><dd>${esc(s.time)}</dd>`);
      if (s.seat) rows.push(`<dt>${esc(T('dt_seat'))}</dt><dd>${esc(s.seat)}</dd>`);
      if (s.price) rows.push(`<dt>${esc(T('dt_price'))}</dt><dd>${esc(window.MMFmtPrice ? window.MMFmtPrice(s.price, s.cur) : `${s.price} ${s.cur || ''}`)}</dd>`);
      const durl = s.url && safeUrl(s.url);
      if (durl) rows.push(`<dt>${esc(T('dt_link'))}</dt><dd><a href="${esc(durl)}" target="_blank" rel="noopener noreferrer" style="color:#e3b23c;text-decoration:none;border-bottom:1px solid currentColor">${esc((durl.match(/^https?:\/\/([^\/]+)/) || [])[1] || T('dt_open_link'))} ↗</a></dd>`);
      document.getElementById('dt-dl').innerHTML = rows.join('');
      document.getElementById('dt-note').textContent = '';
      document.getElementById('dt-note').style.display = 'none';
      if (dlg.showModal) dlg.showModal();
    }
    document.getElementById('dtclose').onclick = () => dlg.close();
    dlg.addEventListener('click', e => { if (e.target === dlg) dlg.close(); });

    /* theme picker */
    function applyTheme(t) {
      if (t === 'midnight') document.documentElement.removeAttribute('data-theme');
      else document.documentElement.setAttribute('data-theme', t);
      try { localStorage.setItem('mm-theme', t); } catch (e) {}
      document.querySelectorAll('#themePick button').forEach(b => b.setAttribute('aria-pressed', b.dataset.th === t));
      drawMap();
    }
    const tp = document.getElementById('themePick');
    if (tp) tp.addEventListener('click', e => { const b = e.target.closest('button'); if (b) applyTheme(b.dataset.th); });

    /* init */
    renderPoster(); buildCityList(); drawMap(); placePins(); moveThumb();
    applyTheme((function () { try { return localStorage.getItem('mm-theme') || 'cream'; } catch (e) { return 'cream'; } })());   // 預設 cream:fallback 若是 midnight 會蓋掉 no-flash 的 cream 且寫進 localStorage,讓「只看公開頁的新訪客」永久卡深色(自家瀏覽器因逛過 me.html 已存 cream 而看不出來)
    window.addEventListener('load', () => { drawMap(); placePins(); moveThumb(); });
    requestAnimationFrame(() => { drawMap(); placePins(); moveThumb(); });
  }

  /* ============================================================================
     BOOT — resolve handle → profile gate → RPC rows → map to MM.shows → render
     ========================================================================== */
  async function boot() {
    // handle 來源:?u= 參數(GitHub Pages 直連)或 window.MM_HANDLE(my. 子網域 Cloudflare Worker 注入,見 worker/)
    const rawHandle = new URLSearchParams(location.search).get('u') || window.MM_HANDLE || '';
    const handle = String(rawHandle).trim().toLowerCase();   // handle 一律小寫存（訪客打 Danny 也要命中 danny）
    if (!cfg.READY || !handle || typeof supabase === 'undefined') { showEmpty(); return; }
    const sb = supabase.createClient(cfg.SUPABASE_URL, cfg.SUPABASE_ANON_KEY);

    // profile gate
    const { data: prof, error: pErr } = await sb.from('profiles')
      .select('id, display_name, is_public').eq('handle', handle).maybeSingle();
    if (pErr || !prof || !prof.is_public) {
      // 查無 → 可能是改名前的舊網址：resolve_handle 解析成現用名並轉過去（舊分享連結永久有效）。
      // RPC 未部署（migration 未跑）→ 靜默略過，照舊顯示 not-found。
      try {
        const { data: nh } = await sb.rpc('resolve_handle', { p_handle: handle });
        // my. 子網域用乾淨路徑 /newhandle(舊版 pathname+'?u=' 在 my. 會變 /oldhandle?u=newhandle 髒網址,
        // 且 u.html 的 canonical 清理只在 apex 網域跑,永不修正,2026-07-10)
        if (nh && nh !== handle) {
          const onMy = /(^|\.)my\./i.test(location.hostname) || location.hostname.indexOf('my.') === 0;
          location.replace(onMy ? '/' + encodeURIComponent(nh) : location.pathname + '?u=' + encodeURIComponent(nh));
          return;
        }
      } catch (e) {}
      showEmpty(); return;
    }

    // catalog (posters + zh names + venue upgrade); failure is non-fatal
    let cat = { titles: [], posters: {}, productions: {}, venues: [] };
    try { cat = await fetch('data/venues_catalog.json').then(r => r.json()); } catch (e) { console.warn('catalog', e); }
    buildCatalogMaps(cat);

    // read-only sightings via SECURITY DEFINER RPC (owner's price/seat privacy flags applied server-side)
    const { data: rows, error: rpcErr } = await sb.rpc('public_sightings', { p_handle: handle });
    // 到這裡 prof 已通過 gate(存在且公開)。rpcErr=真錯誤→not-found;rows 空但無錯=帳號公開但 0 筆→'none'
    if (rpcErr) { console.warn('public_sightings', rpcErr); showEmpty(); return; }
    if (!rows || !rows.length) { showEmpty('none'); return; }
    upgradeVenueNames(rows, cat);

    // map each row → me.html S-show shape
    const mapped = rows.map(row => {
      const k = (row.title || '').toLowerCase();
      const prec = row.precision || precisionOf(row.seen_date);
      return {
        id: row.id, title: row.title || '?', zh: MS(ZH_BY_TITLE[k] || ''), prod: '', color: '#7c5cff',
        // 公開頁 posterFull 一律走代理(不留原始自訂 URL):否則 proxy 失敗的 onerror/點圖會讓「訪客」瀏覽器直連海報主機
        // → 洩漏訪客 IP/Referer,可被拿來當追蹤信標(牴觸本站不追蹤立場)。owner 自己的 me.html 不受此限。
        poster: resolvePoster(row), posterFull: resolvePoster(row), posterAlt: altPoster(row), posterFit: 'cover', posterBg: null,
        date: partialDate(row.seen_date, prec), precision: prec, time: '',
        venue: window.MMStripCitySuffix(foldVenue(row.venue || ''), row.city || ''), city: foldCity(row.city || ''), country: normCountry(row.country),
        lat: row.lat, lng: row.lng, seat: row.seat || '',
        price: (row.price != null ? String(row.price) : ''), cur: row.currency || '',
        rating: row.rating || 0, fav: !!row.fav, note: '', url: row.url || '', logged: false,   // fav 由 public_sightings RPC 帶出(add_fav.sql)
        tag: TAG_BY_TITLE[k] || '',   // 劇種傳統(catalog 對映;劇迷類型的劇種軸)
      };
    });

    // mutate in place — MM.stats()/recent()/personality() close over this same array
    MM.shows.length = 0; MM.shows.push(...mapped);

    const displayName = prof.display_name || handle;
    document.title = `${displayName} — ${T('doc_title_suffix')}`;   // 「我的音樂劇/My Musicals」依語言(2026-07-10)
    const h1 = document.querySelector('.hero h1'); if (h1) h1.textContent = TN('h1_suffix', { name: displayName });

    render();
  }

  boot();
})();
