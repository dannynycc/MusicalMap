/* mm-strings.js — 足跡側(u.html,之後 me.html)的 UI 字典與語言解析。
   語言決定順序:?hl= 參數(en|zh-hant|zh-hans) → Worker 注入的 window.MM_HL → navigator.language → zh-hant。
   語言必須進網址(?hl=)才能被搜尋引擎分語言收錄(Google 官方指引 + Strava/X 實務,
   見 docs/DESIGN_username_sharing.md);navigator 只是給「沒帶參數的真人」的禮貌預設。
   zh-hans:P1 暫用 zh-hant 字典顯示(未接 OpenCC;主站 chrome 已有此機制,之後統一)。 */
(function () {
  var STR = {
    'zh-hant': {
      // ---- u.html 靜態 ----
      nav_theatres: '所有劇院', nav_map: '演出地圖', nav_create: '＋ 建立你自己的',
      th_midnight: '午夜（暗）', th_gallery: '畫廊白（亮）', th_cream: '節目單奶油（亮）', th_neon: '霓虹（暗）', th_deco: '裝飾金（暗）',
      aria_theme: '主題底色', aria_seg: '檢視模式', aria_sort: '排序', aria_close: '關閉',
      hero_sub: '每看一場，蓋一個章',
      seg_poster: '海報牆', seg_passport: '護照', seg_log: '清單',
      sort_date: '最近觀看', sort_rating: '評分', sort_count: '次數', sort_title: '劇名',
      sec_map: '我的觀劇足跡', sec_map_hint: '點一座城市，只看那裡的收藏',
      aria_zoom_in: '放大', aria_zoom_out: '縮小', aria_zoom_reset: '重置',
      map_hint: '滾輪縮放 · 拖曳平移',
      legend_dot: '圓點 = 看過音樂劇的城市', legend_size: '圓大小 = 看的場數',
      sec_stats: '觀劇統計',
      st_shows: '🎭 最常看的劇', st_countries: '🌏 最常去的國家', st_cities: '🏙 最常去的城市', st_theatres: '🏛 最常去的劇院',
      st_year: '📅 各年', st_month: '📅 各月', st_week: '📅 各星期',
      sec_you: '關於這位劇迷', badges_title: '🏅 成就徽章',
      footer_1: '海報牆與護照，是同一批收藏的兩種看法。',
      footer_2: '封面取自各劇官方與公開資料。想擁有自己的音樂劇護照？',
      footer_cta: '建立你自己的 →',
      empty_title: '找不到這個公開頁', empty_sub: '這個收藏頁不存在，或擁有者尚未公開。',
      empty_cta: '＋ 建立你自己的 My Musicals',
      dt_zoom: '↗ 點圖開新分頁看原圖',
      // ---- u-view.js runtime ----
      bn_musicals: '音樂劇 Musicals', bn_unique: '不同作品 Unique', bn_cities: '城市 Cities', bn_countries: '國家 Countries',
      newest_label: '最新一場', none_yet: '還沒看過任何一場',
      upcoming_dot_n: '· 即將 {n} 場', upcoming_n: '即將 {n} 場',
      chip_all: '全部', ribbon_upcoming: '即將上演', up_mark: '即將<br>上演', up_suffix: '（即將上演）', detail_suffix: ' 詳情',
      n_musicals: '{n} 部音樂劇',
      lt_show: '劇目', lt_city: '城市', lt_date: '日期', lt_rate: '評分', lt_tbd: '未定',
      date_tbd: '日期未定',
      pin_aria: '{city} · {n} 部音樂劇',
      citylist_title: '造訪城市 Cities', citylist_sub: '{c} 座城市 · {k} 國 · 共 {t} 場',
      badge_shows: '{n} 場演出', badge_countries: '{n} 國蓋章', badge_cities: '{n} 座城市',
      badge_unique: '{n} 部不同作品', badge_fav: '{n} 部最愛',
      persona_title: '你是什麼樣的劇迷？',
      dt_venue: '劇院', dt_city: '城市', dt_date: '日期', dt_time: '時間', dt_seat: '座位', dt_price: '票價', dt_link: '連結', dt_open_link: '開啟連結',
      h1_suffix: '{name} 的音樂劇收藏',
      // ---- data.js personality(me/u 共用) ----
      p_G: '環球旅人', p_L: '在地常客', p_Y: '念舊死忠', p_X: '嚐鮮探索',
      p_M: '當代派', p_C: '經典派', p_S: '大製作控', p_I: '小劇場魂',
      p_n_countries: '{n} 國', p_repeat: '重看率 {n}%',
      p_blurb_globe: '你橫跨 {n} 國追劇', p_blurb_local_country: '你在 {n} 個國家看過戲', p_blurb_local_place: '你在 {n} 個地方看過戲',
      p_blurb_loyal: '願意為愛的戲二刷三刷', p_blurb_fresh: '幾乎每齣都嚐鮮',
      p_axis_era: '{m} 現代 / {c} 經典', p_axis_scale: '{s} 大 / {i} 小',
      p_blurb_modern: '口味偏當代', p_blurb_classic: '鍾情經典',
      p_blurb_spectacle: '也擋不住大製作的聲光', p_blurb_intimate: '更愛小劇場的親密',
      p_sep: '，', p_end: '。',
    },
    'en': {
      nav_theatres: 'All Theatres', nav_map: 'Live Map', nav_create: '＋ Create your own',
      th_midnight: 'Midnight (dark)', th_gallery: 'Gallery white (light)', th_cream: 'Playbill cream (light)', th_neon: 'Neon (dark)', th_deco: 'Deco gold (dark)',
      aria_theme: 'Theme', aria_seg: 'View mode', aria_sort: 'Sort', aria_close: 'Close',
      hero_sub: 'One stamp for every show you see',
      seg_poster: 'Posters', seg_passport: 'Passport', seg_log: 'List',
      sort_date: 'Recently seen', sort_rating: 'Rating', sort_count: 'Times seen', sort_title: 'Title',
      sec_map: 'Where I’ve been', sec_map_hint: 'Click a city to see only those shows',
      aria_zoom_in: 'Zoom in', aria_zoom_out: 'Zoom out', aria_zoom_reset: 'Reset',
      map_hint: 'Scroll to zoom · drag to pan',
      legend_dot: 'Dot = a city with shows seen', legend_size: 'Size = number of shows',
      sec_stats: 'Stats',
      st_shows: '🎭 Most-seen shows', st_countries: '🌏 Top countries', st_cities: '🏙 Top cities', st_theatres: '🏛 Top theatres',
      st_year: '📅 By year', st_month: '📅 By month', st_week: '📅 By weekday',
      sec_you: 'About this theatregoer', badges_title: '🏅 Badges',
      footer_1: 'The poster wall and the passport are two views of the same collection.',
      footer_2: 'Artwork comes from each show’s official and public sources. Want your own musical passport?',
      footer_cta: 'Create your own →',
      empty_title: 'This page doesn’t exist', empty_sub: 'It may have been removed, or the owner hasn’t made it public.',
      empty_cta: '＋ Create your own My Musicals',
      dt_zoom: '↗ Open full-size image in a new tab',
      bn_musicals: 'Musicals', bn_unique: 'Unique shows', bn_cities: 'Cities', bn_countries: 'Countries',
      newest_label: 'Latest', none_yet: 'No shows seen yet',
      upcoming_dot_n: '· {n} upcoming', upcoming_n: '{n} upcoming',
      chip_all: 'All', ribbon_upcoming: 'Coming up', up_mark: 'Coming<br>up', up_suffix: ' (upcoming)', detail_suffix: ' details',
      n_musicals: '{n} musicals',
      lt_show: 'Show', lt_city: 'City', lt_date: 'Date', lt_rate: 'Rating', lt_tbd: 'TBD',
      date_tbd: 'Date TBD',
      pin_aria: '{city} · {n} musicals',
      citylist_title: 'Cities visited', citylist_sub: '{c} cities · {k} countries · {t} shows',
      badge_shows: '{n} shows', badge_countries: '{n} countries stamped', badge_cities: '{n} cities',
      badge_unique: '{n} unique shows', badge_fav: '{n} favourites',
      persona_title: 'What kind of theatregoer are you?',
      dt_venue: 'Theatre', dt_city: 'City', dt_date: 'Date', dt_time: 'Time', dt_seat: 'Seat', dt_price: 'Price', dt_link: 'Link', dt_open_link: 'Open link',
      h1_suffix: '{name}’s Musicals',
      p_G: 'Globetrotter', p_L: 'Hometown regular', p_Y: 'Loyal rewatcher', p_X: 'Explorer',
      p_M: 'Modernist', p_C: 'Classicist', p_S: 'Spectacle lover', p_I: 'Small-stage soul',
      p_n_countries: '{n} countries', p_repeat: '{n}% rewatch rate',
      p_blurb_globe: 'You’ve chased shows across {n} countries', p_blurb_local_country: 'You’ve seen shows in {n} countries', p_blurb_local_place: 'You’ve seen shows in {n} place(s)',
      p_blurb_loyal: 'happy to see a beloved show two or three times', p_blurb_fresh: 'almost always trying something new',
      p_axis_era: '{m} modern / {c} classic', p_axis_scale: '{s} big / {i} small',
      p_blurb_modern: 'tastes lean contemporary', p_blurb_classic: 'devoted to the classics',
      p_blurb_spectacle: 'can’t resist a big spectacle', p_blurb_intimate: 'prefers the intimacy of a small stage',
      p_sep: ', ', p_end: '.',
    },
  };

  // ---- 語言解析(?hl 進網址是 SEO 需求;navigator 只服務沒帶參數的真人) ----
  var q = null;
  try { q = new URLSearchParams(location.search).get('hl'); } catch (e) {}
  var hl = (q === 'en' || q === 'zh-hant' || q === 'zh-hans') ? q : null;
  if (!hl && window.MM_HL && STR[window.MM_HL === 'zh-hans' ? 'zh-hant' : window.MM_HL]) hl = window.MM_HL; // Worker 注入
  if (!hl) {
    var nl = (navigator.language || '').toLowerCase();
    if (nl.indexOf('zh') === 0) hl = (nl.indexOf('cn') > -1 || nl.indexOf('hans') > -1 || nl.indexOf('sg') > -1) ? 'zh-hans' : 'zh-hant';
    else if (nl) hl = 'en';
    else hl = 'zh-hant';
  }
  var D = STR[hl === 'zh-hans' ? 'zh-hant' : hl] || STR['zh-hant'];

  window.MM_STR = STR;
  window.MM_HL = hl;
  window.MM_T = function (k) {
    if (D[k] != null) return D[k];
    if (STR['zh-hant'][k] != null) return STR['zh-hant'][k];
    return k;
  };

  // ---- 套用到靜態 DOM:data-i18n(textContent)/-title/-aria;<html lang>;語言切換 pills ----
  function apply() {
    document.documentElement.lang = hl === 'en' ? 'en' : (hl === 'zh-hans' ? 'zh-Hans' : 'zh-Hant');
    document.querySelectorAll('[data-i18n]').forEach(function (el) { el.textContent = window.MM_T(el.getAttribute('data-i18n')); });
    document.querySelectorAll('[data-i18n-title]').forEach(function (el) { el.title = window.MM_T(el.getAttribute('data-i18n-title')); });
    document.querySelectorAll('[data-i18n-aria]').forEach(function (el) { el.setAttribute('aria-label', window.MM_T(el.getAttribute('data-i18n-aria'))); });
    // 語言切換:改寫 ?hl= 並保留其他參數(如 ?u=)——連結而非按鈕,爬蟲也能發現語言變體
    document.querySelectorAll('[data-hl-link]').forEach(function (a) {
      var t = a.getAttribute('data-hl-link');
      var u = new URL(location.href);
      if (t === 'zh-hant') u.searchParams.delete('hl'); else u.searchParams.set('hl', t);
      a.href = u.pathname + (u.search || '');
      var active = (t === hl) || (t === 'zh-hant' && hl === 'zh-hans');
      if (active) a.setAttribute('aria-current', 'true');
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', apply);
  else apply();
  window.MM_APPLY_I18N = apply;
})();
