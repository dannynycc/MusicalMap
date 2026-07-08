// Build-time generator of the tri-URL site: /en/, /zh-hans/, /zh-hant/ (+ root router,
// sitemap, robots). Run from repo root AFTER gen_variants.mjs: `node build/gen_site.mjs`.
//
// Each variant page is PRERENDERED: the show list + JSON-LD are baked into static HTML so
// Google and (JS-blind) AI crawlers see real content. The Leaflet app then hydrates on top
// for humans, reading the matching data variant. Shared js/css/data load via absolute
// root paths (custom domain serves the repo at /).
import fs from "fs";
import crypto from "crypto";

const BASE = "/";
const SITE = "https://themusicalmap.com";
const VARIANTS = {
  "en":      { lang: "en",      hreflang: "en",      label: "MusicalMap — Live World Map of Musicals",
               desc: "Musicals playing around the world right now — Broadway, West End, tours and original productions across 40+ countries." },
  "zh-hans": { lang: "zh-Hans", hreflang: "zh-Hans", label: "MusicalMap — 全球音乐剧实时地图",
               desc: "此刻全球正在上演的音乐剧实时地图：百老汇、西区、巡演与各国原创音乐剧，涵盖 40+ 国家，每日更新。" },
  "zh-hant": { lang: "zh-Hant", hreflang: "zh-Hant", label: "MusicalMap — 全球音樂劇即時地圖",
               desc: "此刻全球正在上演的音樂劇即時地圖：百老匯、西區、巡演與各國原創音樂劇,涵蓋 40+ 國家,每日更新。" },
};
const esc = (s) => String(s == null ? "" : s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
const JSONLD_CAP = 300; // cap Event ItemList; full text list is unbounded (cheap)
// cache-bust token for js/css so returning visitors never run a stale app.js (the bug
// where a cached old app.js fetched a relative data path and showed an empty map). Token
// is a content hash of the actual assets → it changes IFF the js/css change.
const ASSETS = ["js/app.js", "js/i18n.js", "js/config.js", "js/mm-acct-menu.js", "css/style.css"];
const VER = (() => {
  const h = crypto.createHash("md5");
  for (const p of ASSETS) h.update(fs.readFileSync(p));
  return h.digest("hex").slice(0, 10);
})();

function hreflangLinks() {
  return [
    `<link rel="alternate" hreflang="en" href="${SITE}/en/" />`,
    `<link rel="alternate" hreflang="zh-Hans" href="${SITE}/zh-hans/" />`,
    `<link rel="alternate" hreflang="zh-Hant" href="${SITE}/zh-hant/" />`,
    `<link rel="alternate" hreflang="x-default" href="${SITE}/" />`,
  ].join("\n  ");
}

function jsonLd(variant, shows) {
  const v = VARIANTS[variant];
  // 只有具備 startDate 的場次才吐成 Event —— schema.org Event 的 startDate 是必填,缺了會被
  // Google Search Console 判為重大錯誤(功能無法進搜尋)。缺 start_date 的場次仍在地圖上,只是
  // 不進結構化資料。同時補上 Google 建議的欄位(eventStatus/image/description/offers),都用真資料;
  // performer(卡司)無來源資料故不填(不捏造)。
  const items = shows.filter((s) => s.start_date).slice(0, JSONLD_CAP).map((s, i) => {
    const ticket = (s.ticket_links && s.ticket_links[0] && s.ticket_links[0].url) || s.ticket_url || undefined;
    const where = s.venue ? `${s.venue}${s.city ? ", " + s.city : ""}` : (s.city || "");
    const ev = {
      "@type": "Event", "name": s.title,
      "startDate": s.start_date, "endDate": s.end_date || undefined,
      "eventStatus": "https://schema.org/EventScheduled",
      "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
      "location": { "@type": "Place", "name": s.venue || s.city,
        "address": { "@type": "PostalAddress", "addressLocality": s.city, "addressCountry": s.country } },
      "image": s.image || undefined,
      "description": where ? `${s.title} — live stage musical at ${where}.` : `${s.title} — live stage musical.`,
      "offers": ticket ? { "@type": "Offer", "url": ticket, "availability": "https://schema.org/InStock", "validFrom": s.start_date } : undefined,
      "url": ticket,
    };
    return { "@type": "ListItem", "position": i + 1, "item": ev };
  });
  const app = {
    "@context": "https://schema.org", "@type": "WebApplication", "name": "MusicalMap",
    "alternateName": v.label, "url": `${SITE}/${variant}/`, "description": v.desc,
    "applicationCategory": "EntertainmentApplication", "operatingSystem": "Web",
    "inLanguage": v.hreflang, "isAccessibleForFree": true,
    "offers": { "@type": "Offer", "price": "0", "priceCurrency": "USD" },
  };
  const list = { "@context": "https://schema.org", "@type": "ItemList",
    "name": v.label, "numberOfItems": items.length, "itemListElement": items };
  // Organization + WebSite entity signals. Google/AI 一度把品牌認成既有的 "Musicmap"
  // (musicmap.info,講音樂流派史的另一站);明確宣告 name/alternateName/url/logo 幫助
  // 知識圖譜把 MusicalMap 建成獨立實體。@id 用網域錨定,三語頁指向同一實體。
  const org = { "@context": "https://schema.org", "@type": "Organization",
    "@id": `${SITE}/#organization`, "name": "MusicalMap",
    "alternateName": ["The Musical Map", "themusicalmap"],
    "url": `${SITE}/`, "logo": `${SITE}/favicon-512.png`,
    "description": "MusicalMap is a live, interactive world map of stage musicals currently playing — Broadway, West End, international tours and original productions across 40+ countries. Not affiliated with Musicmap." };
  const site = { "@context": "https://schema.org", "@type": "WebSite",
    "@id": `${SITE}/#website`, "name": "MusicalMap", "alternateName": v.label,
    "url": `${SITE}/`, "inLanguage": v.hreflang,
    "publisher": { "@id": `${SITE}/#organization` }, "description": v.desc };
  return `<script type="application/ld+json">${JSON.stringify(org)}</script>\n  ` +
         `<script type="application/ld+json">${JSON.stringify(site)}</script>\n  ` +
         `<script type="application/ld+json">${JSON.stringify(app)}</script>\n  ` +
         `<script type="application/ld+json">${JSON.stringify(list)}</script>`;
}

// Run-date label, matching the interactive app's fmtDates (js/app.js): open-ended →
// 長期上演 / Now playing; has a closing → 至 {end} / Until; future premiere → {start} 起 /
// From; else blank. Keeps the prerendered SEO list consistent with what humans see.
function runLabel(s, variant) {
  const t = new Date(); t.setHours(0, 0, 0, 0);
  const f = (iso) => { const [y, m, d] = iso.split("-").map(Number); return y === t.getFullYear() ? `${m}/${d}` : `${y}/${m}/${d}`; };
  const en = variant === "en";
  if (s.end_rolling) return en ? "Long-running" : (variant === "zh-hans" ? "长期上演" : "長期上演");
  if (s.end_date) return (en ? "Until " : "至 ") + f(s.end_date);
  if (s.start_date && new Date(s.start_date) > t) return en ? "From " + f(s.start_date) : f(s.start_date) + " 起";
  return "";
}
// Prerendered, crawler-readable show list (the app re-renders #show-list for humans).
function prerenderList(variant, shows) {
  const sep = variant === "en" ? ", " : "、";
  const li = shows.map((s) => {
    const where = [s.venue, s.city, s.country].filter(Boolean).join(sep);
    const url = (s.ticket_links && s.ticket_links[0] && s.ticket_links[0].url) || s.ticket_url || "";
    const dates = runLabel(s, variant);
    const name = url ? `<a href="${esc(url)}" rel="nofollow">${esc(s.title)}</a>` : esc(s.title);
    return `<li>${name} — ${esc(where)}${dates ? ` (${esc(dates)})` : ""}</li>`;
  }).join("\n      ");
  return li;
}

// Globe icon + current short code (繁中 / 简中 / EN) → dropdown of full autonyms on click.
// Collapsed stays compact for the 375px phone header (short code hides < 430px, globe only);
// expanded shows full names. No flags. Behaviour: js/mm-lang.js. Highlight baked at build.
const LANG_GLOBE = '<svg class="lang-globe" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.5 2.5 2.5 15 0 18M12 3c-2.5 2.5-2.5 15 0 18M4.5 7.5c4.5 2.5 10.5 2.5 15 0M4.5 16.5c4.5-2.5 10.5-2.5 15 0"/></svg>';
const LANG_CHEV = '<svg class="lang-chev" viewBox="0 0 24 24" aria-hidden="true"><path d="M5 8l7 7 7-7"/></svg>';
const LANG_TICK = '<svg class="lang-tick" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 12l5 5L20 6"/></svg>';
const LANG_CODE = { "zh-hant": "繁中", "zh-hans": "简中", "en": "EN" };
const LANG_NAME = { "zh-hant": "繁體中文", "zh-hans": "简体中文", "en": "English" };
const LANG_TAG = { "zh-hant": "zh-Hant", "zh-hans": "zh-Hans", "en": "en" };
function langSwitch(active) {
  const opt = (v) =>
    `<a class="lang-opt${v === active ? " active" : ""}" role="menuitem" href="${BASE}${v}/" lang="${LANG_TAG[v]}" hreflang="${LANG_TAG[v]}"${v === active ? ' aria-current="true"' : ""}><span>${LANG_NAME[v]}</span>${LANG_TICK}</a>`;
  return `<div id="lang-switch" role="group" aria-label="Language / 語言">
        <button type="button" class="lang-trigger" aria-haspopup="true" aria-expanded="false" aria-label="選擇語言 / Select language">${LANG_GLOBE}<span class="lang-cur">${LANG_CODE[active]}</span>${LANG_CHEV}</button>
        <div class="lang-pop" role="menu" hidden>
          ${opt("zh-hant")}
          ${opt("zh-hans")}
          ${opt("en")}
        </div>
      </div>`;
}

function page(variant, shows) {
  const v = VARIANTS[variant];
  const t = variant === "en"
    ? { tagline: "Musicals playing around the world right now", theatres: "All theatres", mine: "My Musicals", guide: "Guide",
        maphome: "Map home", search: "Search musicals, cities, theatres…", privacy: "Privacy", terms: "Terms",
        h1: "MusicalMap — Live World Map of Musicals Playing Now", listhdr: "Musicals playing now", filterLabel: "Category" }
    : variant === "zh-hans"
    ? { tagline: "此刻全球正在上演的音乐剧", theatres: "所有剧院", mine: "我的音乐剧", guide: "怎么使用",
        maphome: "地图首页", search: "搜寻音乐剧名、城市、剧院…", privacy: "隐私政策", terms: "使用条款",
        h1: "MusicalMap — 全球此刻正在上演的音乐剧实时地图", listhdr: "正在上演的音乐剧", filterLabel: "分类" }
    : { tagline: "此刻全球正在上演的音樂劇", theatres: "所有劇院", mine: "我的音樂劇", guide: "怎麼使用",
        maphome: "地圖首頁", search: "搜尋音樂劇名、城市、劇院…", privacy: "隱私權政策", terms: "使用條款",
        h1: "MusicalMap — 全球此刻正在上演的音樂劇即時地圖", listhdr: "正在上演的音樂劇", filterLabel: "分類" };
  // zh-hans pages load OpenCC (small t2cn dict) so i18n can simplify the UI chrome strings.
  const openccTag = variant === "zh-hans"
    ? `\n  <script src="https://cdn.jsdelivr.net/npm/opencc-js@1.3.1/dist/umd/t2cn.js" integrity="sha384-P/OaFUnOIAgMkLxsXIAaP6WO3Wm09591cGX5bHbW4eCOeDxH9L8U3aWYf4cE4SYl" crossorigin="anonymous"></script>` : "";
  return `<!DOCTYPE html>
<html lang="${v.lang}">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="referrer" content="strict-origin-when-cross-origin" />
  <meta name='impact-site-verification' value='5862030b-2ad5-46e3-ba52-429cfcca041d'>
  <title>${esc(v.label)}</title>
  <meta name="description" content="${esc(v.desc)}" />
  <link rel="canonical" href="${SITE}/${variant}/" />
  ${hreflangLinks()}
  <meta property="og:type" content="website" />
  <meta property="og:site_name" content="MusicalMap" />
  <meta property="og:title" content="${esc(v.label)}" />
  <meta property="og:description" content="${esc(v.desc)}" />
  <meta property="og:url" content="${SITE}/${variant}/" />
  <meta property="og:image" content="${SITE}/og-image.png" />
  <meta property="og:image:width" content="1200" />
  <meta property="og:image:height" content="630" />
  <meta property="og:image:alt" content="MusicalMap — live world map of musicals" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:image" content="${SITE}/og-image.png" />
  <!-- favicon: Google 只收正方形且 ≥48px 的圖示;舊版指 logo.png(122×200 直式)會被拒→退回地球圖示 -->
  <link rel="icon" href="${BASE}favicon.ico?v=3" sizes="any" />
  <link rel="icon" type="image/svg+xml" href="${BASE}logo.svg" />
  <link rel="icon" type="image/png" sizes="96x96" href="${BASE}favicon-96.png?v=3" />
  <link rel="icon" type="image/png" sizes="192x192" href="${BASE}favicon-192.png?v=3" />
  <link rel="apple-touch-icon" href="${BASE}apple-touch-icon.png?v=3" />
  ${jsonLd(variant, shows)}
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,900&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" integrity="sha384-sHL9NAb7lN7rfvG5lfHpm643Xkcjzp4jFvuavGOndn6pjVqS6ny56CAt3nsEVT4H" crossorigin="anonymous" />
  <link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.css" integrity="sha384-pmjIAcz2bAn0xukfxADbZIb3t8oRT9Sv0rvO+BR5Csr6Dhqq+nZs59P0pPKQJkEV" crossorigin="anonymous" />
  <link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.Default.css" integrity="sha384-wgw+aLYNQ7dlhK47ZPK7FRACiq7ROZwgFNg0m04avm4CaXS+Z9Y7nMu8yNjBKYC+" crossorigin="anonymous" />
  <link rel="stylesheet" href="${BASE}css/style.css?v=${VER}" />
  <script>window.MM_VARIANT="${variant}";window.MM_BASE="${BASE}";</script>${openccTag}
  <script src="${BASE}js/mm-acct-menu.js?v=${VER}" defer></script><!-- 登入過(mm_owner cookie)→「我的音樂劇」CTA 自動換成大頭照選單;未登入照常顯示 CTA -->
  <script src="${BASE}js/mm-lang.js?v=${VER}" defer></script><!-- 語言切換下拉(globe→繁中/简中/English)開關行為 -->

  <!-- Google Analytics(GA4 G-GC07MYC1MY;訪客來源/行為分析。root 路由頁不埋(立即轉走);隱私揭露見 privacy.html §1/§3) -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-GC07MYC1MY"></script>
  <script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','G-GC07MYC1MY');</script>
</head>
<body>
  <header id="topbar">
    <a id="brand" href="${BASE}${variant}/">
      <img class="brand-logo" src="${BASE}logo.svg" alt="" />
      <span class="logo">Musical<span class="logo-em">Map</span></span>
      <span class="tagline">${esc(t.tagline)}</span>
    </a>
    <nav id="topnav">
      ${langSwitch(variant)}
      <a class="nav-link" href="${BASE}${variant}/">${esc(t.maphome)}</a>
      <!-- 所有劇院入口暫藏(2026-07-03 指示;/theatres 頁面保留可直達)
      <a class="nav-link" href="${BASE}theatres?lang=${variant}">${esc(t.theatres)}</a> -->
      <a class="nav-link" href="${BASE}guide?hl=${variant}">${esc(t.guide)}</a>
      <!-- 隱私/條款移到地圖右下 attribution 列(Google Maps 慣例,見 app.js addAttribution) -->
      <a id="mine-link" class="nav-cta" href="https://my.themusicalmap.com/?hl=${variant}">${esc(t.mine)}</a>
    </nav>
  </header>

  <h1 class="sr-only">${esc(t.h1)}</h1>

  <div id="app">
    <aside id="sidebar">
      <div id="controls">
        <input id="search" type="search" placeholder="${esc(t.search)}" autocomplete="off" />
        <div id="count"></div><!-- 本月上演即時計數(app.js 填字);位置=搜尋欄下、#controls 底線上 -->
      </div>
      <!-- prerendered for crawlers (Google + AI bots that don't run JS); the app
           replaces this list on load for interactive users. -->
      <h2 class="sr-only">${esc(t.listhdr)}</h2>
      <ul id="show-list">
      ${prerenderList(variant, shows)}
      </ul>
    </aside>
    <div id="mapcol">
      <div id="filterbar">
        <span class="fb-lbl">${esc(t.filterLabel)}</span>
        <div id="tag-filters" role="group" aria-label="filter"></div>
      </div>
      <main id="map">
        <div id="timebar">
          <button id="time-play" class="tb-btn" title="play">▶</button>
          <button id="time-today" class="tb-btn tb-now" title="today">${variant === "en" ? "This month" : variant === "zh-hans" ? "本月" : "本月"}</button>
          <input id="time-range" type="range" min="0" max="36" value="0" step="1" aria-label="${variant === "en" ? "Month timeline" : "月份時間軸"}" />
          <!-- 原生 month input 的顯示格式跟「瀏覽器語言」走、不理頁面 lang(中文瀏覽器上英文頁會顯示 2026年07月)
               → 蓋一層自己用頁面語言格式化的 label,原生 input 透明墊底只負責點開月曆 -->
          <span id="time-month-wrap"><span id="time-month-label"></span><input id="time-month" type="month" aria-label="month" /></span>
        </div>
      </main>
    </div>
  </div>

  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" integrity="sha384-cxOPjt7s7Iz04uaHJceBmS+qpjv2JkIHNVcuOrM+YHwZOmJGBXI00mdUXEq65HTH" crossorigin="anonymous"></script>
  <script src="https://unpkg.com/leaflet.markercluster@1.5.3/dist/leaflet.markercluster.js" integrity="sha384-eXVCORTRlv4FUUgS/xmOyr66XBVraen8ATNLMESp92FKXLAMiKkerixTiBvXriZr" crossorigin="anonymous"></script>
  <script src="${BASE}js/config.js?v=${VER}"></script>
  <script src="${BASE}js/i18n.js?v=${VER}"></script>
  <script src="${BASE}js/app.js?v=${VER}"></script>
</body>
</html>
`;
}

// Root: a tiny language router (redirect by saved/browser pref) + x-default SEO with
// links to all three variants so crawlers reach them and there's a no-JS fallback.
function rootRouter() {
  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>MusicalMap — Live World Map of Musicals 全球音樂劇即時地圖</title>
  <meta name="description" content="An interactive map of musicals playing around the world right now — Broadway, West End, tours and original productions. 全球正在上演的音樂劇即時地圖。" />
  <link rel="canonical" href="${SITE}/" />
  <link rel="icon" href="${BASE}favicon.ico?v=3" sizes="any" />
  <link rel="icon" type="image/svg+xml" href="${BASE}logo.svg" />
  <link rel="icon" type="image/png" sizes="96x96" href="${BASE}favicon-96.png?v=3" />
  <link rel="apple-touch-icon" href="${BASE}apple-touch-icon.png?v=3" />
  <meta property="og:type" content="website" />
  <meta property="og:site_name" content="MusicalMap" />
  <meta property="og:title" content="MusicalMap — Live World Map of Musicals" />
  <meta property="og:description" content="Musicals playing around the world right now — Broadway, West End, tours and original productions across 40+ countries." />
  <meta property="og:url" content="${SITE}/" />
  <meta property="og:image" content="${SITE}/og-image.png" />
  <meta property="og:image:width" content="1200" />
  <meta property="og:image:height" content="630" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:image" content="${SITE}/og-image.png" />
  <!-- Google「網站名稱」(搜尋結果顯示 MusicalMap 而非網址)要求首頁(root)有 WebSite 結構化資料
       +og:site_name;先前只有 /en/ 等變體頁有、root 沒有 → Google 退回顯示網域。 -->
  <script type="application/ld+json">${JSON.stringify({ "@context": "https://schema.org", "@type": "Organization", "@id": `${SITE}/#organization`, "name": "MusicalMap", "alternateName": ["The Musical Map", "themusicalmap"], "url": `${SITE}/`, "logo": `${SITE}/favicon-512.png` })}</script>
  <script type="application/ld+json">${JSON.stringify({ "@context": "https://schema.org", "@type": "WebSite", "@id": `${SITE}/#website`, "name": "MusicalMap", "alternateName": ["The Musical Map", "themusicalmap"], "url": `${SITE}/`, "publisher": { "@id": `${SITE}/#organization` } })}</script>
  ${hreflangLinks()}
  <script>
    (function () {
      var v = localStorage.getItem("mm_variant");
      if (v !== "en" && v !== "zh-hans" && v !== "zh-hant") {
        var l = (navigator.language || "en").toLowerCase();
        v = l.indexOf("zh") === 0
          ? (l.indexOf("cn") > -1 || l.indexOf("hans") > -1 || l.indexOf("sg") > -1 ? "zh-hans" : "zh-hant")
          : "en";
      }
      location.replace("${BASE}" + v + "/");
    })();
  </script>
</head>
<body>
  <p>MusicalMap — choose your language / 選擇語言:
    <a href="${BASE}zh-hant/">繁體中文</a> ·
    <a href="${BASE}zh-hans/">简体中文</a> ·
    <a href="${BASE}en/">English</a>
  </p>
</body>
</html>
`;
}

function sitemap() {
  // the three indexable language trees, cross-linked by hreflang…
  const variants = ["en", "zh-hans", "zh-hant"].map((v) =>
    `  <url><loc>${SITE}/${v}/</loc>` +
    `<xhtml:link rel="alternate" hreflang="en" href="${SITE}/en/"/>` +
    `<xhtml:link rel="alternate" hreflang="zh-Hans" href="${SITE}/zh-hans/"/>` +
    `<xhtml:link rel="alternate" hreflang="zh-Hant" href="${SITE}/zh-hant/"/>` +
    `<xhtml:link rel="alternate" hreflang="x-default" href="${SITE}/"/></url>`);
  // …plus the standalone pages (kept from the previous sitemap so they stay indexed).
  // me.html 刻意不列:登入閘頁(爬蟲只看到「載入中」),head 已加 noindex;公開內容在 u.html。
  // 無副檔名 canonical:GH Pages 與 Cloudflare Pages 皆直達 200(CF 對 .html 形式會 308 到無副檔名)。
  const pages = ["theatres", "guide", "about", "privacy", "terms"].map(
    (p) => `  <url><loc>${SITE}/${p}</loc></url>`);
  return `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">
${[...variants, ...pages].join("\n")}
</urlset>
`;
}

function robots() {
  // Allow major search + AI/answer-engine crawlers explicitly (variant content only
  // exists for them because pages are prerendered). Compliance is voluntary; declaring
  // intent is the right signal. (Carries over the prior list + adds Claude-SearchBot.)
  const bots = ["Googlebot", "Bingbot", "GPTBot", "OAI-SearchBot", "ChatGPT-User",
                "ClaudeBot", "Claude-Web", "Claude-SearchBot", "PerplexityBot",
                "Google-Extended", "Applebot-Extended"];
  return "# MusicalMap — open to all crawlers, including AI/answer engines.\n" +
         "User-agent: *\nAllow: /\n\n" +
         bots.map((b) => `User-agent: ${b}\nAllow: /`).join("\n\n") +
         `\n\nSitemap: ${SITE}/sitemap.xml\n`;
}

// ---- run ----
for (const variant of Object.keys(VARIANTS)) {
  const shows = JSON.parse(fs.readFileSync(`data/variants/shows.${variant}.json`, "utf8")).shows;
  fs.mkdirSync(variant, { recursive: true });
  fs.writeFileSync(`${variant}/index.html`, page(variant, shows));
  console.log(`${variant.padEnd(8)} → ${variant}/index.html (${shows.length} shows, ${Math.min(shows.length, JSONLD_CAP)} in JSON-LD)`);
}
fs.writeFileSync("index.html", rootRouter());
fs.writeFileSync("sitemap.xml", sitemap());
fs.writeFileSync("robots.txt", robots());
console.log("root index.html (router) + sitemap.xml + robots.txt written");
