/* nav 大頭照選單（monogram＋下拉:我的音樂劇/帳號設定/登出）— 全站共用、全自包（自帶樣式+三語標籤）。
   兩種用法:
   1. autoMount（about/guide/privacy/terms/theatres/index）:載入後自動找 nav 上的「我的音樂劇」CTA,
      有 mm_owner cookie（=登入過）才換成頭像選單;未登入照常顯示 CTA（比登入更有 incentive,使用者指示）。
   2. build()（me.html/settings.html 登入態）:呼叫端傳 letter/連結/onLogout 自行掛載。
   登出一律導 my.themusicalmap.com/settings.html?signout=1（session 住 my. origin,在那裡才能真 signOut）。
   純呈現:不碰 Supabase;innerHTML 只吃檔內模板字串,使用者資料一律 textContent。 */
window.MMAcctMenu = (function () {
  // 三語標籤內建（此元件跨 mm-strings 與 i18n.js 兩套系統的頁面,label 自帶最穩;改字時三處=此處+mm-strings 對應 key 同步）
  var LABELS = {
    'zh-hant': { account: '我的帳號', my: '我的音樂劇', settings: '帳號設定', logout: '登出' },
    'zh-hans': { account: '我的账号', my: '我的音乐剧', settings: '账号设置', logout: '退出登录' },
    'en':      { account: 'My account', my: 'My Musicals', settings: 'Account settings', logout: 'Sign out' }
  };
  function detectLang() {
    try {
      var q = new URLSearchParams(location.search).get('hl');
      if (q === 'en' || q === 'zh-hans' || q === 'zh-hant') return q;
      if (window.MM_HL && LABELS[window.MM_HL]) return window.MM_HL;
      if (window.MM_VARIANT && LABELS[window.MM_VARIANT]) return window.MM_VARIANT;
      var mv = localStorage.getItem('mm_variant');
      if (mv && LABELS[mv]) return mv;
      var l = (document.documentElement.lang || '').toLowerCase();
      if (l.indexOf('en') === 0) return 'en';
      if (l === 'zh-hans') return 'zh-hans';
      if (l) return 'zh-hant';
      var nl = (navigator.language || '').toLowerCase();
      if (nl.indexOf('zh') === 0) return (nl.indexOf('cn') > -1 || nl.indexOf('hans') > -1 || nl.indexOf('sg') > -1) ? 'zh-hans' : 'zh-hant';
      return nl ? 'en' : 'zh-hant';
    } catch (e) { return 'zh-hant'; }
  }
  function readOwnerCookie() {
    try { var m = document.cookie.match(/(?:^|;\s*)mm_owner=([^;]+)/); return m ? decodeURIComponent(m[1]) : ''; }
    catch (e) { return ''; }
  }
  // Google 頭像 URL(me.html/settings.html 登入時種的 mm_av cookie;只給本人 nav 顯示,不進公開頁)
  function readAvatarCookie() {
    try {
      var m = document.cookie.match(/(?:^|;\s*)mm_av=([^;]+)/); if (!m) return '';
      var u = decodeURIComponent(m[1]);
      return /^https:\/\/[a-z0-9.-]+\.(googleusercontent|gstatic)\.com\//.test(u) ? u : '';   // 只信 Google 圖床,防 cookie 被塞奇怪網址
    } catch (e) { return ''; }
  }
  var CSS = '.acmenu{position:relative;display:inline-flex}' +
    '.acmenu-btn{position:relative;overflow:hidden;width:34px;height:34px;border-radius:50%;display:grid;place-items:center;cursor:pointer;font-family:var(--fr,Fraunces,Georgia,serif);font-weight:900;font-size:16px;color:var(--gold,#a07a34);text-transform:uppercase;background:color-mix(in srgb,var(--gold,#a07a34) 14%,transparent);border:1.5px solid color-mix(in srgb,var(--gold,#a07a34) 55%,transparent);transition:box-shadow .15s;padding:0;line-height:1}' +
    '.acmenu-btn:hover,.acmenu-btn[aria-expanded="true"]{box-shadow:0 0 0 3px color-mix(in srgb,var(--gold,#a07a34) 18%,transparent)}' +
    '.acmenu-av{position:absolute;inset:0;width:100%;height:100%;border-radius:50%;object-fit:cover;display:block}' +   /* 絕對定位:grid auto 軌內 height:100% 解析不到定值會照圖片比例撐爆 */
    '.acmenu-pop{position:absolute;top:calc(100% + 8px);right:0;min-width:172px;z-index:2600;padding:6px;background:var(--s1,var(--paper,#fffdf7));border:1px solid var(--hair2,rgba(90,80,60,.28));border-radius:12px;box-shadow:0 16px 44px rgba(0,0,0,.28)}' +
    '.acmenu-pop[hidden]{display:none}' +
    '.acmenu-it{display:block;padding:9px 12px;border-radius:8px;font-size:13.5px;font-weight:600;color:var(--ink1,var(--text,#221f18));text-decoration:none;opacity:1}' +
    '.acmenu-it:hover{background:color-mix(in srgb,var(--gold,#a07a34) 12%,transparent);color:var(--gold,#a07a34);opacity:1}' +
    '.acmenu-sep{height:1px;margin:5px 8px;background:var(--hair2,rgba(90,80,60,.22))}';
  var cssDone = false;
  function injectCss() {
    if (cssDone) return; cssDone = true;
    var s = document.createElement('style'); s.textContent = CSS; document.head.appendChild(s);
  }
  function el(html) { var t = document.createElement('template'); t.innerHTML = html.trim(); return t.content.firstChild; }

  /* o = { letter, avatar?, lang?, labels?, links:{my,settings}, onLogout? }  onLogout 缺省=導 my./settings.html?signout=1 */
  function build(o) {
    injectCss();
    var L = o.labels || LABELS[o.lang || detectLang()] || LABELS['zh-hant'];
    var wrap = el('<div class="acmenu"></div>');
    var btn = el('<button type="button" class="acmenu-btn" aria-haspopup="menu" aria-expanded="false"></button>');
    btn.setAttribute('aria-label', L.account); btn.title = L.account;
    btn.textContent = (String(o.letter || '?').trim().charAt(0) || '?').toUpperCase();
    if (o.avatar) {   // Google 大頭貼;載入失敗(過期/擋圖)自動退回首字母
      var im = new Image();
      im.className = 'acmenu-av'; im.alt = ''; im.referrerPolicy = 'no-referrer';
      im.onload = function () { btn.textContent = ''; btn.appendChild(im); };
      im.src = o.avatar;
    }
    var menu = el('<div class="acmenu-pop" role="menu" hidden></div>');
    function item(label, href, onclick) {
      var a = el('<a class="acmenu-it" role="menuitem"></a>');
      a.textContent = label;
      if (onclick) { a.href = '#'; a.addEventListener('click', function (e) { e.preventDefault(); close(); onclick(); }); }
      else a.href = href;
      return a;
    }
    menu.appendChild(item(L.my, o.links.my));
    menu.appendChild(item(L.settings, o.links.settings));
    menu.appendChild(el('<div class="acmenu-sep"></div>'));
    var signoutUrl = 'https://my.themusicalmap.com/settings.html?signout=1';
    if (o.onLogout) menu.appendChild(item(L.logout, null, o.onLogout));
    else menu.appendChild(item(L.logout, signoutUrl));
    wrap.appendChild(btn); wrap.appendChild(menu);
    function onDoc(e) { if (!wrap.contains(e.target)) close(); }
    function close() { if (menu.hidden) return; menu.hidden = true; btn.setAttribute('aria-expanded', 'false'); document.removeEventListener('click', onDoc, true); }
    btn.addEventListener('click', function () {
      var open = menu.hidden;
      menu.hidden = !open; btn.setAttribute('aria-expanded', open ? 'true' : 'false');
      if (open) document.addEventListener('click', onDoc, true);
    });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') close(); });
    return wrap;
  }

  /* 自動掛載:登入過(mm_owner cookie)→ 把 nav 上的「我的音樂劇」CTA 換成頭像選單;未登入不動 */
  function autoMount() {
    var h = readOwnerCookie(); if (!h) return;
    var cta = document.querySelector('#mine-link') ||
      document.querySelector('a.nav-cta[href^="https://my.themusicalmap.com"],a.cta[href^="https://my.themusicalmap.com"]');
    if (!cta) return;
    var lang = detectLang(), hl = '?hl=' + lang;
    cta.replaceWith(build({
      letter: h.charAt(0), avatar: readAvatarCookie(), lang: lang,
      links: { my: 'https://my.themusicalmap.com/' + encodeURIComponent(h) + hl, settings: 'https://my.themusicalmap.com/settings.html' + hl }
    }));
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', autoMount);
  else autoMount();

  return { readOwnerCookie: readOwnerCookie, build: build, detectLang: detectLang };
})();
