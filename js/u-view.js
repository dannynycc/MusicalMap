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

  // 中文頁：國家名繁中；劇院名只取中文部分 + 去廳別後綴(大/中/小劇院…)、臺→台。
  const COUNTRY_ZH = { 'United States': '美國', 'USA': '美國', 'United Kingdom': '英國', 'UK': '英國', 'Taiwan': '台灣', 'Japan': '日本', 'South Korea': '南韓', 'China': '中國', 'Hong Kong': '香港', 'Macau': '澳門', 'Singapore': '新加坡', 'Australia': '澳洲', 'New Zealand': '紐西蘭', 'Canada': '加拿大', 'Germany': '德國', 'France': '法國', 'Austria': '奧地利', 'Switzerland': '瑞士', 'Spain': '西班牙', 'Italy': '義大利', 'Netherlands': '荷蘭', 'Belgium': '比利時', 'Sweden': '瑞典', 'Norway': '挪威', 'Denmark': '丹麥', 'Finland': '芬蘭', 'Ireland': '愛爾蘭', 'Poland': '波蘭', 'Czech Republic': '捷克', 'Hungary': '匈牙利', 'Portugal': '葡萄牙', 'Mexico': '墨西哥', 'Brazil': '巴西', 'Argentina': '阿根廷', 'United Arab Emirates': '阿聯', 'UAE': '阿聯', 'Philippines': '菲律賓', 'Malaysia': '馬來西亞', 'Thailand': '泰國', 'Indonesia': '印尼', 'India': '印度', 'Israel': '以色列', 'Turkey': '土耳其', 'South Africa': '南非', 'Russia': '俄羅斯', 'Vietnam': '越南', 'Ukraine': '烏克蘭', 'Bulgaria': '保加利亞', 'Chile': '智利', 'Colombia': '哥倫比亞', 'Croatia': '克羅埃西亞', 'Egypt': '埃及', 'Estonia': '愛沙尼亞', 'Greece': '希臘', 'Jersey': '澤西島', 'Latvia': '拉脫維亞', 'Lithuania': '立陶宛', 'Peru': '秘魯', 'Romania': '羅馬尼亞', 'Serbia': '塞爾維亞', 'Slovakia': '斯洛伐克', 'Slovenia': '斯洛維尼亞' };
  const countryZh = (c) => COUNTRY_ZH[c] || c || '';
  const _cjk = /[぀-ヿ㐀-鿿가-힯豈-﫿]/;
  const _HALL = new Set(['大劇院', '中劇院', '小劇院', '大劇場', '中劇場', '小劇場', '音樂廳', '演奏廳', '戲劇廳', '歌劇廳', '演藝廳', '表演廳', '實驗劇場', '排練場', '大廳', '小廳']);
  const venueZh = (v) => { if (!v) return v || ''; const t = String(v).split(/\s+/).filter((x) => _cjk.test(x)); if (!t.length) return v; const core = t.filter((x) => !_HALL.has(x)); return (core.length ? core : t).join(' ').replace(/臺/g, '台'); };

  /* ---- catalog-driven poster + zh-name resolution (mirrors js/u.js) ---- */
  let POSTER_BY_TITLE = {};   // title(lower) -> poster url
  let PRODUCTION_BY_KEY = {}; // production_key -> {poster,…}
  let ZH_BY_TITLE = {};       // en title(lower) -> zh name
  function posterFor(t) { return POSTER_BY_TITLE[(t || '').toLowerCase()] || null; }
  // 自訂海報常是原始大圖 → 走免費即時縮圖代理 wsrv.nl(寬600+webp)加速；catalog 官方圖不動。
  function proxyImg(u) { if (!u || !/^https?:\/\//i.test(u) || /(wsrv\.nl|weserv\.nl)/i.test(u)) return u;
    if (/[?&]w=\d/i.test(u) || /\bi\d?\.wp\.com\b/i.test(u)) return u;   // 已是縮圖 CDN/含寬度參數 → 不代理
    return 'https://wsrv.nl/?url=' + encodeURIComponent(u) + '&w=600&output=webp&q=82'; }
  function resolvePoster(s) {
    if (s.poster_override && safeUrl(s.poster_override)) return proxyImg(s.poster_override);
    const p = s.production_key && PRODUCTION_BY_KEY[s.production_key];
    if (p && p.poster) return p.poster;
    return posterFor(s.title);
  }
  function buildCatalogMaps(cat) {
    Object.values(cat.productions || {}).forEach((arr) => arr.forEach((p) => { PRODUCTION_BY_KEY[p.key] = p; }));
    (cat.titles || []).forEach((t) => {
      const p = cat.posters ? cat.posters[t.group] : null;
      if (t.en) { const k = t.en.toLowerCase(); if (p) POSTER_BY_TITLE[k] = p; if (t.zh) ZH_BY_TITLE[k] = t.zh; }
      if (t.zh && p) POSTER_BY_TITLE[t.zh.toLowerCase()] = p;
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
  }

  /* RPC seen_date (full) + precision → the partial date string me.html expects */
  function precisionOf(seen) { if (!seen) return 'none'; const d = String(seen); return d.length === 4 ? 'year' : d.length === 7 ? 'month' : 'day'; }
  function partialDate(seen, prec) { if (!seen) return ''; const p = prec || precisionOf(seen); if (p === 'year') return seen.slice(0, 4); if (p === 'month') return seen.slice(0, 7); return seen; }

  /* ---- empty / not-found ---- */
  function showEmpty() {
    const w = document.getElementById('pub-wrap'); if (w) w.style.display = 'none';
    const e = document.getElementById('pub-empty'); if (e) e.hidden = false;
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
    const fdt = d => { if (!d) return '日期未定'; const [y, m, dd] = d.split('-');
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
      [['<b>' + st.total + '</b>', '音樂劇 Musicals'], [st.unique, '不同作品 Unique'], [st.cities, '城市 Cities'], [st.countries, '國家 Countries']]
        .forEach(([n, l]) => { const d = document.createElement('div'); d.className = 'bn'; d.innerHTML = `<div class="n tnum">${n}</div><div class="l">${l}</div>`; bn.appendChild(d); });
      const newest = MM.recent(true)[0];   // 只取已發生的最近一場
      const up = stAll.upcoming || 0;
      const upTxt = up > 0 ? ` <span class="nw" style="color:var(--gold)">· 即將 ${up} 場</span>` : '';
      document.getElementById('newest').innerHTML = newest
        ? `<span class="dot"></span><span class="nw">最新一場 <b>${esc(newest.title)}</b></span> <span class="nw">${esc(newest.city)}${newest.date ? ' · ' + fshort(newest.date) : ''}</span>${upTxt}`
        : (up > 0 ? `<span class="dot"></span><span class="nw">還沒看過任何一場</span><span class="nw" style="color:var(--gold)">即將 ${up} 場</span>` : '');
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
          <img alt="${esc(s.title)} poster" loading="lazy" decoding="async" ${s.posterFit === 'contain' ? 'style="object-fit:contain;object-position:center"' : ''}/>
          <figcaption class="fallback"><span class="kick">A Musical</span><span class="ft">${esc(s.title)}</span><span class="fzh">${esc(s.zh)}</span><span class="rule"></span></figcaption>
          <div class="topfx"></div>
          ${fut ? `<div class="up-veil"></div><div class="up-ribbon">即將上演</div>` : ''}
          <span class="flag">${FLAG[s.country] || ''}</span>${s.fav ? '<span class="fav">❤️</span>' : ''}
        </figure>
        <div class="cap"><span class="cap-t"><span class="en">${esc(s.title)}</span><span class="zh">${esc(s.zh)}</span></span>
          <div class="cap-venue">${esc(venueZh(s.venue) || '')}</div>
          <div class="cap-where">${esc([cityName(s.city), countryZh(s.country)].filter(Boolean).join(' · '))}</div>
          <div class="cap-date">${esc(s.date ? s.date.replace(/-/g, '/') : '')}</div></div>`;
      const img = c.querySelector('img'), fig = c.querySelector('.poster'), skel = c.querySelector('.skel');
      let _retried = false;
      img.onload = () => { img.classList.add('ready'); skel.style.display = 'none'; };
      img.onerror = () => { if (!_retried && s.posterFull && s.posterFull !== s.poster) { _retried = true; img.src = s.posterFull; return; } fig.classList.add('is-fallback'); };   // 代理失敗→退回原圖→都失敗才色塊
      img.src = s.poster || '';
      if (!s.poster) fig.classList.add('is-fallback');
      c.onclick = () => openDetail(s);
      return c;
    }
    function renderPoster() {
      const w = document.getElementById('wall-poster'); w.innerHTML = '';
      const list = filtered();
      list.forEach((s, i) => { const el = posterEl(s); el.classList.add('reveal'); el.style.setProperty('--i', i % 12); w.appendChild(el); io.observe(el); });
      document.getElementById('count').textContent = `${list.length} 部音樂劇`;
    }
    /* ---------- LOG LIST VIEW ---------- */
    function renderLog() {
      const el = document.getElementById('wall-log'); const list = filtered();
      document.getElementById('count').textContent = `${list.length} 部音樂劇`;
      el.innerHTML = `<div class="logtable" role="table">
        <div class="lt-head" role="row"><span>劇目</span><span>城市</span><span>日期</span><span>評分</span></div>` +
        list.map(s => `<button class="lt-row" data-id="${s.id}" role="row">
          <span class="lt-show"><span class="lt-thumb">${s.poster ? `<img src="${esc(s.poster)}" referrerpolicy="no-referrer" alt=""/>` : `<i>${esc((s.title || '?').trim()[0] || '?')}</i>`}</span>
            <span class="lt-t"><b>${esc(s.title)}</b>${s.zh ? `<i>${esc(s.zh)}</i>` : ''}</span></span>
          <span class="lt-city">${s.city ? esc(cityName(s.city)) : '<span class="muted">—</span>'} ${s.country ? (FLAG[s.country] || '') : ''}</span>
          <span class="lt-date">${fshort(s.date) || '<span class="muted">未定</span>'}</span>
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
      return `<svg viewBox="0 0 128 128" style="--rot:${rot}deg">
        <defs><path id="${id}t" d="${top}"/><path id="${id}b" d="${bot}"/></defs>
        <circle cx="64" cy="64" r="56" fill="none" stroke="currentColor" stroke-width="2.4"/>
        <circle cx="64" cy="64" r="48" fill="none" stroke="currentColor" stroke-width="1"/>
        <text font-size="10.5" letter-spacing="1.2" fill="currentColor" font-family="Inter,sans-serif" font-weight="700">
          <textPath href="#${id}t" startOffset="50%" text-anchor="middle">${esc(enTitle)}</textPath></text>
        <text font-size="8" letter-spacing="1" fill="currentColor" font-family="Inter,sans-serif">
          <textPath href="#${id}b" startOffset="50%" text-anchor="middle">${esc(s.city.toUpperCase())} · ${esc(venueCode(s.venue))}</textPath></text>
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
      document.getElementById('count').textContent = `${list.length} 部音樂劇`;
      const byC = {}; list.forEach(s => { (byC[s.country] = byC[s.country] || []).push(s); });
      const order = Object.keys(byC).sort((a, b) => byC[b].length - byC[a].length);
      order.forEach(co => {
        const arr = byC[co].sort((a, b) => a.date.localeCompare(b.date));
        const cities = [...new Set(arr.map(s => s.city))].join(' · ');
        const stamped = arr.filter(s => !isFut(s.date)).length;   // 只算已到場的戳章數
        const v = document.createElement('div'); v.className = 'visa reveal';
        v.innerHTML = `<div class="crow"><span class="cn">${esc(countryZh(co))}</span>
          <span class="ct">${esc(cities)}</span><span class="prog">${stamped} STAMP${stamped !== 1 ? 'S' : ''}</span></div>
          <div class="stamps">${arr.map((s, j) => {
            const dly = Math.min(j * 0.05, 0.5).toFixed(2); const mile = milestoneFor(s, j, j === 0); const fut = isFut(s.date);
            return `<div class="stamp${fut ? ' is-future' : ''}" data-sid="${s.id}" role="button" tabindex="0" aria-label="${esc((s.title || '') + (fut ? '（即將上演）' : '') + ' 詳情')}" style="--ink:${esc(s.color)};--rot:${(((s.id * 37) % 9) - 4)}deg;--dly:${dly}s">
              ${mile && !fut ? `<span class="mile">${mile}</span>` : ''}${stampSvg(s)}${fut ? '<span class="up-mark">即將<br>上演</span>' : ''}</div>`; }).join('')}</div>`;
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
      ['全部', ...stAll.years].forEach((y, i) => { const b = document.createElement('button'); b.className = 'chip'; b.textContent = y; b.setAttribute('aria-pressed', i === 0);
        b.onclick = () => { activeYear = y; activeCity = null; [...c.children].forEach(x => x.setAttribute('aria-pressed', 'false')); b.setAttribute('aria-pressed', 'true'); rerender(); }; c.appendChild(b); }); })();
    document.getElementById('sort').onchange = e => { sortBy = e.target.value; rerender(); };
    function rerender() { mode === 'poster' ? renderPoster() : mode === 'passport' ? renderPassport() : renderLog(); }

    /* scroll reveal */
    const io = new IntersectionObserver(es => { es.forEach(e => { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } }); }, { rootMargin: '0px 0px -8% 0px', threshold: .08 });
    document.querySelectorAll('.reveal').forEach(el => io.observe(el));

    /* ---------- MAP ---------- */
    const CITYZH = {"Aarhus": "奧胡斯", "Adelaide": "阿得雷德", "Aichi": "愛知", "Albuquerque": "阿布奎基", "Amsterdam": "阿姆斯特丹", "Antwerp": "安特衛普", "Atlanta": "亞特蘭大", "Auckland": "奧克蘭", "Austin": "奧斯汀", "Baltimore": "巴爾的摩", "Barcelona": "巴塞隆納", "Beijing": "北京", "Belfast": "貝爾法斯特", "Berlin": "柏林", "Birmingham": "伯明罕", "Boston": "波士頓", "Brighton": "布萊頓", "Brisbane": "布里斯本", "Bristol": "布里斯托", "Brussels": "布魯塞爾", "Budapest": "布達佩斯", "Buenos Aires": "布宜諾斯艾利斯", "Buffalo": "水牛城", "Calgary": "卡加利", "Cambridge": "劍橋", "Cardiff": "卡地夫", "Changsha": "長沙", "Changzhou": "常州", "Charlotte": "夏洛特", "Chengdu": "成都", "Chiayi": "嘉義", "Chicago": "芝加哥", "Chongqing": "重慶", "Cincinnati": "辛辛那提", "Cleveland": "克里夫蘭", "Cologne": "科隆", "Columbus": "哥倫布", "Copenhagen": "哥本哈根", "Daegu": "大邱", "Dallas": "達拉斯", "Denver": "丹佛", "Detroit": "底特律", "Dongguan": "東莞", "Dubai": "杜拜", "Dublin": "都柏林", "Edinburgh": "愛丁堡", "Edmonton": "愛德蒙頓", "Firenze": "佛羅倫斯", "Fort Lauderdale": "羅德岱堡", "Fort Worth": "沃斯堡", "Frankfurt": "法蘭克福", "Fukuoka": "福岡", "Fuzhou": "福州", "Ghent": "根特", "Gifu": "岐阜", "Glasgow": "格拉斯哥", "Gothenburg": "哥德堡", "Grand Rapids": "大急流城", "Guangzhou": "廣州", "Göteborg": "哥德堡", "Haikou": "海口", "Hamburg": "漢堡", "Hangzhou": "杭州", "Harbin": "哈爾濱", "Hefei": "合肥", "Helsinki": "赫爾辛基", "Hengyang": "衡陽", "Hiroshima": "廣島", "Houston": "休士頓", "Hsinchu": "新竹", "Hyogo": "兵庫", "Jiaxing": "嘉興", "Jinan": "濟南", "Kanagawa": "神奈川", "Kansas City": "堪薩斯城", "Kaohsiung": "高雄", "Kunshan": "崑山", "Köln": "科隆", "København": "哥本哈根", "København V": "哥本哈根", "Langfang": "廊坊", "Las Vegas": "拉斯維加斯", "Leeds": "里茲", "Liverpool": "利物浦", "London": "倫敦", "Los Angeles": "洛杉磯", "Louisville": "路易斯維爾", "Lyon": "里昂", "Madison": "麥迪遜", "Madrid": "馬德里", "Maihama": "舞濱", "Manchester": "曼徹斯特", "Melbourne": "墨爾本", "Memphis": "曼菲斯", "Mexico City": "墨西哥市", "Miami": "邁阿密", "Milano": "米蘭", "Milwaukee": "密爾瓦基", "Minneapolis": "明尼阿波利斯", "Monterrey": "蒙特雷", "Montreal": "蒙特婁", "Munich": "慕尼黑", "México": "墨西哥市", "München": "慕尼黑", "Nagoya": "名古屋", "Nanchang": "南昌", "Nanjing": "南京", "Nanning": "南寧", "Nantong": "南通", "Napoli": "拿坡里", "Nashville": "納許維爾", "New Orleans": "紐奧良", "New Taipei": "新北", "New York": "紐約", "Newcastle": "紐卡索", "Ningbo": "寧波", "Nottingham": "諾丁罕", "Oklahoma City": "奧克拉荷馬市", "Omaha": "奧馬哈", "Orlando": "奧蘭多", "Osaka": "大阪", "Oslo": "奧斯陸", "Ottawa": "渥太華", "Oxford": "牛津", "Padova": "帕多瓦", "Paris": "巴黎", "Penghu": "澎湖", "Perth": "伯斯", "Philadelphia": "費城", "Phoenix": "鳳凰城", "Pingtung": "屏東", "Pittsburgh": "匹茲堡", "Portland": "波特蘭", "Prague": "布拉格", "Praha": "布拉格", "Providence": "普羅維登斯", "Qidong": "啓東", "Qingdao": "青島", "Quzhou": "衢州", "Richmond": "里奇蒙", "Rio de Janeiro": "里約熱內盧", "Roma": "羅馬", "Rotterdam": "鹿特丹", "Salt Lake City": "鹽湖城", "San Antonio": "聖安東尼奧", "San Diego": "聖地牙哥", "San Francisco": "舊金山", "San Jose": "聖荷西", "Sapporo": "札幌", "Seattle": "西雅圖", "Seoul": "首爾", "Shanghai": "上海", "Sheffield": "雪菲爾", "Shenyang": "瀋陽", "Shenzhen": "深圳", "Singapore": "新加坡", "St. Louis": "聖路易", "Stockholm": "斯德哥爾摩", "Stuttgart": "斯圖加特", "Suzhou": "蘇州", "Swansea": "斯旺西", "Sydney": "雪梨", "São Paulo": "聖保羅", "Taichung": "台中", "Taipei": "台北", "Taitung": "台東", "Taiyuan": "太原", "Taizhou": "台州", "Takarazuka (兵庫)": "寶塚", "Tampa": "坦帕", "Tianjin": "天津", "Tokyo": "東京", "Tokyo (日比谷)": "東京", "Torino": "杜林", "Toronto": "多倫多", "Utrecht": "烏特勒支", "Vancouver": "溫哥華", "Vienna": "維也納", "Warsaw": "華沙", "Warszawa": "華沙", "Washington": "華盛頓", "Weifang": "濰坊", "Wellington": "威靈頓", "Wien": "維也納", "Wimbledon": "溫布頓", "Wuhan": "武漢", "Wuxi": "無錫", "Xi'an": "西安", "Yantai": "煙台", "Yinchuan": "銀川", "Yokohama": "橫濱", "York": "約克", "Yunlin": "雲林", "Zhengzhou": "鄭州", "Zhuhai": "珠海", "Zhuji": "諸暨", "Zibo": "淄博", "Zurich": "蘇黎世", "Zürich": "蘇黎世", "连云港": "連雲港"};
    function cityName(c) { if (!c) return c; const base = String(c).replace(/,\s*[A-Za-z.]{2,}$/, '').trim(); return CITYZH[c] || CITYZH[base] || c; }
    function cityHasZh(c) { return cityName(c) !== c; }
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
        el.setAttribute('aria-label', `${c.city} · ${c.n} 部音樂劇`);
        el.innerHTML = `<span class="glow" style="width:${sz * 2.4}px;height:${sz * 2.4}px"></span>
          <span class="ring"></span>
          <span class="core" style="width:${sz}px;height:${sz}px">${c.n}</span>
          <span class="lbl">${esc(cityName(c.city))}</span>`;
        el.onclick = () => filterToCity(c.city);
        pins.appendChild(el); PINS.push({ el, px, py });
      });
      positionPins();
    }
    function positionPins() { PINS.forEach(p => { const [sx, sy] = tf(p.px, p.py);
      if (sx < -0.01 || sx > 1.01 || sy < -0.01 || sy > 1.01) { p.el.style.display = 'none'; }
      else { p.el.style.display = ''; p.el.style.left = sx * 100 + '%'; p.el.style.top = sy * 100 + '%'; } }); }
    function buildCityList() {
      const el = document.getElementById('citylist');
      const byCity = {}; S.forEach(s => { if (!s.city || isFut(s.date)) return; (byCity[s.city] = byCity[s.city] || { ...s, n: 0 }).n++; });   // 地圖/城市榜只算已到場
      const arr = Object.values(byCity).sort((a, b) => b.n - a.n);
      el.innerHTML = `<h4>造訪城市 Cities</h4><div class="sh">${arr.length} 座城市 · ${st.countries} 國 · 共 ${st.total} 場</div>` +
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
      let drag = null;
      wrap.addEventListener('pointerdown', e => { if (e.target.closest('.pin') || e.target.closest('.mapzoom')) return;
        drag = { x: e.clientX, y: e.clientY }; try { wrap.setPointerCapture(e.pointerId); } catch (_) {} wrap.classList.add('grabbing'); });
      wrap.addEventListener('pointermove', e => { if (!drag) return; const r = wrap.getBoundingClientRect();
        mapV.x -= (e.clientX - drag.x) / (r.width * mapV.z); mapV.y -= (e.clientY - drag.y) / (r.height * mapV.z); drag = { x: e.clientX, y: e.clientY }; clampV(); renderMap(); });
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
      const tops = st.topShows[0];
      const badges = [['🎭', `${st.total} 場演出`, true], ['🌏', `${st.countries} 國蓋章`, st.countries >= 3], ['🏙', `${st.cities} 座城市`, false], ['🎬', `${st.unique} 部不同作品`, false]];
      if (tops && tops[1] > 1) badges.push(['🔁', `${tops[0]} ×${tops[1]}`, false]);
      if (st.favCount > 0) badges.push(['❤️', `${st.favCount} 部最愛`, false]);
      b.innerHTML = badges.map(([ic, t, g]) => `<div class="badge ${g ? 'gold' : ''}"><span class="ic">${ic}</span>${t}</div>`).join('');
      function barList(id, items, fmt) { const el = document.getElementById(id); if (!el) return;
        if (!items || !items.length) { el.innerHTML = '<div class="sl-empty">—</div>'; return; }
        const mx = items[0][1] || 1;
        el.innerHTML = items.slice(0, 6).map(([k, v]) => `<div class="sl-row"><span class="sl-k" title="${esc(k)}">${esc(fmt ? fmt(k) : k)}</span><span class="sl-bar"><i style="width:${Math.max(6, v / mx * 100)}%"></i></span><span class="sl-v">${v}</span></div>`).join(''); }
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
            scales: { y: { beginAtZero: true, ticks: { precision: 0, color: tc }, grid: { color: g }, border: { color: g } },
                      x: { ticks: { color: tc }, grid: { color: g }, border: { color: g } } } } });
      }
      const validYears = (st.years || []).filter(y => y && !isNaN(+y)).map(Number);
      let yLabels = [], yVals = [];
      if (validYears.length) { const cnt = {}; (st.perYear || []).forEach(([y, n]) => { if (y && !isNaN(+y)) cnt[+y] = n; });
        const y0 = Math.min(...validYears), y1 = Math.max(...validYears);
        for (let y = y0; y <= y1; y++) { yLabels.push('' + y); yVals.push(cnt[y] || 0); } }
      lineChart('ch-year', yLabels, yVals);
      lineChart('ch-month', (st.perMonth || []).map(x => x[0]), (st.perMonth || []).map(x => x[1]));
      lineChart('ch-week', (st.perWeekday || []).map(x => x[0]), (st.perWeekday || []).map(x => x[1]));
      const p = MM.personality();
      document.getElementById('persona').innerHTML = `<h3>你是什麼樣的劇迷？</h3>
        <div class="pn">${p.nickname}</div><div class="pb">${p.blurb}</div>
        <div class="axes">${p.axes.map(a => { const left = a[2]; const pos = left ? 14 : 86;
          return `<div class="axis"><div class="r"><span class="${left ? 'on' : ''}">${a[0]}</span><span>${a[3]}</span><span class="${!left ? 'on' : ''}">${a[1]}</span></div><div class="track"><i style="left:calc(${pos}% - 6px)"></i></div></div>`; }).join('')}</div>`;
    })();

    /* ---------- detail modal (read-only) ---------- */
    const dlg = document.getElementById('detail');
    function openDetail(s) {
      const dp = document.getElementById('dt-poster'), img = document.getElementById('dt-img');
      if (s.poster) { dp.classList.remove('is-fallback');
        img.style.objectFit = s.posterFit === 'contain' ? 'contain' : 'cover';
        if (img.getAttribute('src') !== s.poster) {
          img.classList.remove('ready'); let _dtr = false;
          img.onload = () => img.classList.add('ready');
          img.onerror = () => { if (!_dtr && s.posterFull && s.posterFull !== s.poster) { _dtr = true; img.src = s.posterFull; return; } img.classList.add('ready'); };  // 代理失敗→退回原圖
          img.src = s.poster;
        } else img.classList.add('ready'); }
      else { dp.classList.add('is-fallback'); img.removeAttribute('src'); dp.style.setProperty('--dt-accent', s.color || '#7c5cff');
        document.getElementById('dt-fb-en').textContent = s.title; document.getElementById('dt-fb-zh').textContent = s.zh || ''; }
      dp.onclick = () => { const full = s.posterFull || s.poster; if (full) window.open(full, '_blank', 'noopener'); };   // 點海報→開新分頁直接顯示原始高解析大圖
      dp.style.cursor = s.poster ? 'zoom-in' : 'default';
      document.getElementById('dt-en').textContent = s.title;
      document.getElementById('dt-zh').textContent = s.zh;
      const rt = document.getElementById('dt-rate');
      if (s.rating > 0) { rt.textContent = stars(s.rating) + `  ${s.rating}/5`; rt.style.display = ''; }
      else { rt.textContent = ''; rt.style.display = 'none'; }
      // 唯讀：座位/票價只在有值時顯示（公開頁隱私由 RPC 決定回不回傳）
      const rows = [
        `<dt>劇院</dt><dd>${esc(venueZh(s.venue) || '—')}</dd>`,
        `<dt>城市</dt><dd>${s.city ? esc(cityName(s.city) + (s.country ? ', ' + countryZh(s.country) : '')) : esc(countryZh(s.country) || '—')} ${FLAG[s.country] || ''}</dd>`,
        `<dt>日期</dt><dd>${esc(s.date ? s.date.replace(/-/g, '/') : '—')}</dd>`,
      ];
      if (s.time) rows.push(`<dt>時間</dt><dd>${esc(s.time)}</dd>`);
      if (s.seat) rows.push(`<dt>座位</dt><dd>${esc(s.seat)}</dd>`);
      if (s.price) rows.push(`<dt>票價</dt><dd>${esc(s.price)} ${esc(s.cur || '')}</dd>`);
      const durl = s.url && safeUrl(s.url);
      if (durl) rows.push(`<dt>連結</dt><dd><a href="${esc(durl)}" target="_blank" rel="noopener noreferrer" style="color:#e3b23c;text-decoration:none;border-bottom:1px solid currentColor">${esc((durl.match(/^https?:\/\/([^\/]+)/) || [])[1] || '開啟連結')} ↗</a></dd>`);
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
    applyTheme((function () { try { return localStorage.getItem('mm-theme') || 'midnight'; } catch (e) { return 'midnight'; } })());
    window.addEventListener('load', () => { drawMap(); placePins(); moveThumb(); });
    requestAnimationFrame(() => { drawMap(); placePins(); moveThumb(); });
  }

  /* ============================================================================
     BOOT — resolve handle → profile gate → RPC rows → map to MM.shows → render
     ========================================================================== */
  async function boot() {
    const rawHandle = new URLSearchParams(location.search).get('u');
    const handle = (rawHandle || '').trim().toLowerCase();   // handle 一律小寫存（訪客打 Danny 也要命中 danny）
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
        if (nh && nh !== handle) { location.replace(location.pathname + '?u=' + encodeURIComponent(nh)); return; }
      } catch (e) {}
      showEmpty(); return;
    }

    // catalog (posters + zh names + venue upgrade); failure is non-fatal
    let cat = { titles: [], posters: {}, productions: {}, venues: [] };
    try { cat = await fetch('data/venues_catalog.json').then(r => r.json()); } catch (e) { console.warn('catalog', e); }
    buildCatalogMaps(cat);

    // read-only sightings via SECURITY DEFINER RPC (owner's price/seat privacy flags applied server-side)
    const { data: rows, error: rpcErr } = await sb.rpc('public_sightings', { p_handle: handle });
    if (rpcErr || !rows || !rows.length) { console.warn('public_sightings', rpcErr); showEmpty(); return; }
    upgradeVenueNames(rows, cat);

    // map each row → me.html S-show shape
    const mapped = rows.map(row => {
      const k = (row.title || '').toLowerCase();
      const prec = row.precision || precisionOf(row.seen_date);
      return {
        id: row.id, title: row.title || '?', zh: ZH_BY_TITLE[k] || '', prod: '', color: '#7c5cff',
        poster: resolvePoster(row), posterFull: (row.poster_override && safeUrl(row.poster_override)) || resolvePoster(row), posterFit: 'cover', posterBg: null,
        date: partialDate(row.seen_date, prec), precision: prec, time: '',
        venue: row.venue || '', city: row.city || '', country: normCountry(row.country),
        lat: row.lat, lng: row.lng, seat: row.seat || '',
        price: (row.price != null ? String(row.price) : ''), cur: row.currency || '',
        rating: row.rating || 0, fav: false, note: '', url: row.url || '', logged: false,
      };
    });

    // mutate in place — MM.stats()/recent()/personality() close over this same array
    MM.shows.length = 0; MM.shows.push(...mapped);

    const displayName = prof.display_name || handle;
    document.title = `${displayName} — My Musicals`;
    const h1 = document.querySelector('.hero h1'); if (h1) h1.textContent = `${displayName} 的音樂劇收藏`;

    render();
  }

  boot();
})();
