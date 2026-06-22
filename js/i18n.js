/* MusicalMap i18n — zh-Hant / English UI strings.
 * Default language follows the browser (zh* → 中文, else English); a header toggle
 * overrides it and is remembered in localStorage. app.js reads t()/LANG and re-renders
 * on the "mm-langchange" event. SHOW DATA (titles, cities) is not translated here —
 * only chrome/UI text. */
(function () {
  const DICT = {
    zh: {
      doc_title: "MusicalMap — 全球音樂劇即時地圖",
      tagline: "此刻全球正在上演的音樂劇",
      nav_theatres: "🎭 所有劇院",
      nav_mine: "⭐ 我的音樂劇足跡",
      search_ph: "搜尋劇名、城市、劇院…",
      play_title: "自動播放時間軸（每月）",
      today: "本月",
      today_title: "回到本月",
      privacy: "隱私權政策",
      terms: "使用條款",
      lang_toggle: "EN",            // label shows the OTHER language you can switch to
      map: "地圖",
      satellite: "衛星",
      "tag_Broadway/West End": "百老匯/西區",
      "tag_德奧音樂劇": "德奧音樂劇",
      "tag_法式音樂劇": "法語音樂劇",
      "tag_西語音樂劇": "西語音樂劇",
      "tag_葡語音樂劇": "葡語音樂劇",
      "tag_中國原創": "中國音樂劇",
      "tag_台灣原創": "台灣音樂劇",
      "tag_日本原創": "日本音樂劇",
      "tag_韓國原創": "韓國音樂劇",
      "tag_歐陸原創": "歐陸其他",
      onsale_until: "售票中至 {d}",
      onsale: "售票中",
      runs_from_sale: "自 {s} 上演 · 售票至 {e}",
      sale_until: "售票至 {e}",
      run_range: "{s} – {e}",
      runs_from: "自 {s} 上演",
      runs_until: "演至 {e}",
      official: "官網",
      tickets: "售票",
      buy_official: "前往官網購票 →",
      buy_tickets: "前往售票頁 →",
      unverified_demo: "⚠ 未驗證（示範資料）",
      unverified: "未驗證",
      empty_title: "沒有符合的音樂劇",
      empty_sub: "試試清除搜尋或開啟其他篩選",
      playing_this_month: "本月上演",
      playing_in: "{ym} 上演",
      count: "{label}：{groups} 部音樂劇 · {n} 個地點",
      loc_count: "{n} 個地點",
      loc_short: "{n} 地",
      updated: "更新於 {d}",
      sources: "{u} · 來源：Broadway · West End · 巡演 · 國際 · Ticketmaster",
      load_error: "⚠ 無法載入 data/shows.json（需用本機 server 開啟，見 README）",
      // theatres.html
      tagline_theatres: "全球音樂劇場館地圖",
      nav_map: "🗺 演出地圖",
      search_ph_theatres: "搜尋劇院、城市…（中／英／原文皆可）",
      v_count: "{n} 個劇院",
      v_count_filtered: "{n} 個劇院（共 {total}）",
      v_more: "…還有 {n} 個，請再縮小搜尋",
      load_error_venues: "⚠ 無法載入場館資料（需用本機 server 開啟）",
      doc_title_theatres: "所有劇院 — MusicalMap",
      // me.html / u.html
      doc_title_me: "我的音樂劇足跡 — MusicalMap",
      nav_global_map: "🗺 演出地圖",
      me_signin: "用 Google 登入",
      me_signout: "登出",
      me_hero_title: "我的音樂劇足跡",
      me_hero_p: "記錄你看過的每一齣音樂劇 —— 自動生成你的 Top 劇目、城市、劇院,年／月／星期趨勢,以及你足跡的個人地圖。",
      me_signin_start: "用 Google 登入開始",
      me_cfg_warn: "⚠ 後端尚未設定（見 docs/SETUP_ACCOUNTS.md）。",
      me_make_public: "公開我的個人檔案",
      me_handle_ph: "你的名稱",
      me_save: "儲存",
      me_copy: "複製",
      me_copied: "已複製！",
      me_top_shows: "最常看的劇",
      me_top_countries: "最常去的國家",
      me_top_cities: "最常去的城市",
      me_top_theatres: "最常去的劇院",
      me_per_year: "各年",
      me_per_month: "各月",
      me_per_weekday: "各星期",
      me_log: "我的紀錄",
      me_no_entries: "還沒有紀錄 —— 點「＋ 新增一齣」。",
      me_add: "＋ 新增一齣",
      me_form_add: "新增一齣音樂劇",
      me_form_edit: "編輯音樂劇",
      me_f_title: "劇名",
      me_title_ph: "輸入中文或英文 type EN or 中文",
      me_f_version: "版本／製作",
      me_version_any: "— 通用／不確定 —",
      me_f_poster: "海報網址（選填）",
      me_poster_ph: "自訂海報網址 custom poster URL",
      me_f_date: "日期",
      me_f_time: "時間",
      me_f_venue: "劇院",
      me_f_city: "城市",
      me_f_country: "國家",
      me_f_seat: "座位",
      me_seat_ph: "例：一樓 A12",
      me_f_price: "票價",
      me_f_currency: "幣別",
      me_f_links: "連結（選填）",
      me_add_link: "＋ 新增連結",
      me_link_ph: "https://… 官網／售票頁",
      me_f_note: "備註",
      me_cancel: "取消",
      me_edit: "編輯",
      me_delete: "刪除",
      me_confirm_del: "確定刪除這筆紀錄？",
      me_t_shows: "看過場次",
      me_t_musicals: "音樂劇數",
      me_t_countries: "國家數",
      me_t_cities: "城市數",
      me_t_theatres: "劇院數",
      me_no_data: "尚無資料",
      me_pick_name: "請先為公開連結取一個名稱。",
      me_name_taken: "這個名稱被用了，換一個試試。",
      me_save_fail: "儲存失敗：",
      me_public_share: "已公開！分享：",
      me_backend_warn: "後端尚未設定 —— 見 docs/SETUP_ACCOUNTS.md",
      // u.html (public profile)
      u_create: "＋ 建立你自己的",
      u_tab_overview: "📊 總覽",
      u_tab_log: "📋 紀錄",
      u_not_found: "找不到此檔案",
      u_not_found_sub: "此檔案不存在或未公開。",
      u_create_big: "建立你自己的音樂劇足跡",
      u_profile: "{name} · 音樂劇足跡",
      u_worldwide: "看過 {n} 場演出（全球）",
      me_col_link: "連結",
      me_col_price: "票價",
    },
    en: {
      doc_title: "MusicalMap — live world map of musicals",
      tagline: "Musicals playing around the world right now",
      nav_theatres: "🎭 All Theatres",
      nav_mine: "⭐ My Musicals",
      search_ph: "Search shows, cities, venues…",
      play_title: "Auto-play the timeline (monthly)",
      today: "Now",
      today_title: "Back to this month",
      privacy: "Privacy",
      terms: "Terms",
      lang_toggle: "中",
      map: "Map",
      satellite: "Satellite",
      "tag_Broadway/West End": "Broadway/West End",
      "tag_德奧音樂劇": "German/Austrian",
      "tag_法式音樂劇": "French",
      "tag_西語音樂劇": "Spanish",
      "tag_葡語音樂劇": "Portuguese",
      "tag_中國原創": "Chinese",
      "tag_台灣原創": "Taiwanese",
      "tag_日本原創": "Japanese",
      "tag_韓國原創": "Korean",
      "tag_歐陸原創": "Other European",
      onsale_until: "On sale through {d}",
      onsale: "On sale",
      runs_from_sale: "From {s} · on sale through {e}",
      sale_until: "On sale through {e}",
      run_range: "{s} – {e}",
      runs_from: "From {s}",
      runs_until: "Until {e}",
      official: "Official",
      tickets: "Tickets",
      buy_official: "Official tickets →",
      buy_tickets: "Get tickets →",
      unverified_demo: "⚠ Unverified (sample data)",
      unverified: "unverified",
      empty_title: "No musicals match",
      empty_sub: "Try clearing the search or your filters",
      playing_this_month: "Playing this month",
      playing_in: "Playing in {ym}",
      count: "{label}: {groups} musicals · {n} locations",
      loc_count: "{n} locations",
      loc_short: "{n} cities",
      updated: "Updated {d}",
      sources: "{u} · Sources: Broadway · West End · Tours · International · Ticketmaster",
      load_error: "⚠ Couldn't load data/shows.json (serve over a local server — see README)",
      // theatres.html
      tagline_theatres: "World map of musical theatres",
      nav_map: "🗺 Show map",
      search_ph_theatres: "Search theatres, cities… (EN / 中文 / native)",
      v_count: "{n} theatres",
      v_count_filtered: "{n} theatres (of {total})",
      v_more: "…and {n} more — narrow your search",
      load_error_venues: "⚠ Couldn't load venue data (serve over a local server)",
      doc_title_theatres: "All Theatres — MusicalMap",
      // me.html / u.html
      doc_title_me: "My Musicals — MusicalMap",
      nav_global_map: "🗺 Global map",
      me_signin: "Sign in with Google",
      me_signout: "Sign out",
      me_hero_title: "My Musicals",
      me_hero_p: "Log every musical you've seen — and get your own Top shows, cities & theatres, year / month / weekday trends, and a personal map of where you've been.",
      me_signin_start: "Sign in with Google to start",
      me_cfg_warn: "⚠ Backend not configured yet (see docs/SETUP_ACCOUNTS.md).",
      me_make_public: "Make my profile public",
      me_handle_ph: "your-name",
      me_save: "Save",
      me_copy: "Copy",
      me_copied: "Copied!",
      me_top_shows: "Top Musicals",
      me_top_countries: "Top Countries",
      me_top_cities: "Top Cities",
      me_top_theatres: "Top Theatres",
      me_per_year: "Per Year",
      me_per_month: "Per Month",
      me_per_weekday: "Per Weekday",
      me_log: "My Log",
      me_no_entries: "No entries yet — click “＋ Add a musical”.",
      me_add: "＋ Add a musical",
      me_form_add: "Add a musical",
      me_form_edit: "Edit musical",
      me_f_title: "Musical",
      me_title_ph: "Type EN or 中文",
      me_f_version: "Version / Production",
      me_version_any: "— Generic / not sure —",
      me_f_poster: "Poster URL (optional)",
      me_poster_ph: "Custom poster URL",
      me_f_date: "Date",
      me_f_time: "Time",
      me_f_venue: "Theatre",
      me_f_city: "City",
      me_f_country: "Country",
      me_f_seat: "Seat",
      me_seat_ph: "e.g. Stalls A12",
      me_f_price: "Price",
      me_f_currency: "Currency",
      me_f_links: "Links (optional)",
      me_add_link: "＋ add link",
      me_link_ph: "https://… official site / ticket page",
      me_f_note: "Note",
      me_cancel: "Cancel",
      me_edit: "Edit",
      me_delete: "Delete",
      me_confirm_del: "Delete this entry?",
      me_t_shows: "Shows seen",
      me_t_musicals: "Musicals",
      me_t_countries: "Countries",
      me_t_cities: "Cities",
      me_t_theatres: "Theatres",
      me_no_data: "No data yet",
      me_pick_name: "Pick a username for your public link first.",
      me_name_taken: "That username is taken — try another.",
      me_save_fail: "Save failed: ",
      me_public_share: "Public! Share: ",
      me_backend_warn: "Backend not configured yet — see docs/SETUP_ACCOUNTS.md",
      // u.html (public profile)
      u_create: "＋ Create your own",
      u_tab_overview: "📊 Overview",
      u_tab_log: "📋 Log",
      u_not_found: "Profile not found",
      u_not_found_sub: "This profile doesn’t exist or isn’t public.",
      u_create_big: "Create your own My Musicals",
      u_profile: "{name} · My Musicals",
      u_worldwide: "{n} shows seen worldwide",
      me_col_link: "Link",
      me_col_price: "Price",
    },
  };

  // Priority: ?lang= URL param (the SEO-indexable per-language URL) > saved choice >
  // browser language. The URL param wins so hreflang links resolve to a stable language
  // and shared links keep their language.
  const urlLang = new URLSearchParams(location.search).get("lang");
  let LANG = (urlLang === "zh" || urlLang === "en") ? urlLang : localStorage.getItem("mm_lang");
  if (LANG !== "zh" && LANG !== "en") LANG = (navigator.language || "en").toLowerCase().startsWith("zh") ? "zh" : "en";

  function t(key, vars) {
    let s = (DICT[LANG] && DICT[LANG][key]) ?? (DICT.en[key]) ?? key;
    if (vars) for (const k in vars) s = s.replace(new RegExp("\\{" + k + "\\}", "g"), vars[k]);
    return s;
  }

  // Localised "month year" for a Date — "2026年06月" vs "Jun 2026".
  function fmtYM(d) {
    return LANG === "zh"
      ? `${d.getFullYear()}年${String(d.getMonth() + 1).padStart(2, "0")}月`
      : d.toLocaleDateString("en-US", { month: "short", year: "numeric" });
  }

  // Apply to static markup: data-i18n (textContent), data-i18n-ph (placeholder),
  // data-i18n-title (title attribute).
  function applyStatic(root) {
    (root || document).querySelectorAll("[data-i18n]").forEach((el) => { el.textContent = t(el.dataset.i18n); });
    (root || document).querySelectorAll("[data-i18n-ph]").forEach((el) => { el.placeholder = t(el.dataset.i18nPh); });
    (root || document).querySelectorAll("[data-i18n-title]").forEach((el) => { el.title = t(el.dataset.i18nTitle); });
    document.documentElement.lang = LANG === "zh" ? "zh-Hant" : "en";
    // segmented switch: highlight the active language (autonyms stay as authored)
    document.querySelectorAll("#lang-switch .lang-opt").forEach((b) => {
      const on = b.dataset.lang === LANG;
      b.classList.toggle("active", on);
      b.setAttribute("aria-pressed", on ? "true" : "false");
    });
    const titleKey = document.documentElement.dataset.titleKey || "doc_title";
    document.title = t(titleKey);
  }

  function setLang(l) {
    LANG = (l === "zh") ? "zh" : "en";
    localStorage.setItem("mm_lang", LANG);
    // reflect language in the URL (?lang=) so it's shareable + matches hreflang, and
    // keep the canonical/og:url self-referencing for the chosen language.
    try {
      const u = new URL(location.href);
      u.searchParams.set("lang", LANG);
      history.replaceState(null, "", u);
      const can = document.querySelector('link[rel="canonical"]');
      if (can) can.setAttribute("href", u.origin + u.pathname + "?lang=" + LANG);
    } catch (e) { /* ignore */ }
    applyStatic();
    window.dispatchEvent(new Event("mm-langchange"));
  }

  // expose
  window.I18N = { t, fmtYM, applyStatic, setLang, get lang() { return LANG; } };
  window.t = t;

  document.addEventListener("DOMContentLoaded", () => {
    applyStatic();
    document.querySelectorAll("#lang-switch .lang-opt").forEach((b) =>
      b.addEventListener("click", () => { if (b.dataset.lang !== LANG) setLang(b.dataset.lang); }));
  });
})();
