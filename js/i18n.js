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
      "tag_Broadway/West End": "Broadway/West End",
      "tag_德奧音樂劇": "德奧音樂劇",
      "tag_法式音樂劇": "法式音樂劇",
      "tag_西語音樂劇": "西語音樂劇",
      "tag_中國原創": "中國原創",
      "tag_台灣原創": "台灣原創",
      "tag_日本原創": "日本原創",
      "tag_韓國原創": "韓國原創",
      "tag_歐陸原創": "歐陸原創",
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
      "tag_西語音樂劇": "Spanish-language",
      "tag_中國原創": "Chinese",
      "tag_台灣原創": "Taiwanese",
      "tag_日本原創": "Japanese",
      "tag_韓國原創": "Korean",
      "tag_歐陸原創": "European",
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
    if (DICT[LANG].doc_title) document.title = t("doc_title");
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
