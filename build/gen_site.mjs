// Build-time generator of the tri-URL site: /en/, /zh-hans/, /zh-hant/ (+ root router,
// sitemap, robots). Run from repo root AFTER gen_variants.mjs: `node build/gen_site.mjs`.
//
// Each variant page is PRERENDERED: the show list + JSON-LD are baked into static HTML so
// Google and (JS-blind) AI crawlers see real content. The Leaflet app then hydrates on top
// for humans, reading the matching data variant. Shared js/css/data load via absolute
// /MusicalMap/ paths so the page works from a subdirectory.
import fs from "fs";
import crypto from "crypto";

const BASE = "/MusicalMap/";
const SITE = "https://dannynycc.github.io/MusicalMap";
const VARIANTS = {
  "en":      { lang: "en",      hreflang: "en",      label: "MusicalMap — live world map of musicals",
               desc: "Musicals playing around the world right now — Broadway, West End, tours and original productions across 40+ countries." },
  "zh-hans": { lang: "zh-Hans", hreflang: "zh-Hans", label: "MusicalMap — 全球音乐剧即时地图",
               desc: "此刻全球正在上演的音乐剧即时地图：百老汇、西区、巡演与各国原创音乐剧，涵盖 40+ 国家，每日更新。" },
  "zh-hant": { lang: "zh-Hant", hreflang: "zh-Hant", label: "MusicalMap — 全球音樂劇即時地圖",
               desc: "此刻全球正在上演的音樂劇即時地圖：百老匯、西區、巡演與各國原創音樂劇,涵蓋 40+ 國家,每日更新。" },
};
const esc = (s) => String(s == null ? "" : s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
const JSONLD_CAP = 300; // cap Event ItemList; full text list is unbounded (cheap)
// cache-bust token for js/css so returning visitors never run a stale app.js (the bug
// where a cached old app.js fetched a relative data path and showed an empty map). Token
// is a content hash of the actual assets → it changes IFF the js/css change.
const ASSETS = ["js/app.js", "js/i18n.js", "js/config.js", "css/style.css"];
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
  const items = shows.slice(0, JSONLD_CAP).map((s, i) => {
    const ev = {
      "@type": "Event", "position": i + 1, "name": s.title,
      "startDate": s.start_date || undefined, "endDate": s.end_date || undefined,
      "location": { "@type": "Place", "name": s.venue || s.city,
        "address": { "@type": "PostalAddress", "addressLocality": s.city, "addressCountry": s.country } },
      "url": (s.ticket_links && s.ticket_links[0] && s.ticket_links[0].url) || s.ticket_url || undefined,
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
  return `<script type="application/ld+json">${JSON.stringify(app)}</script>\n  ` +
         `<script type="application/ld+json">${JSON.stringify(list)}</script>`;
}

// Prerendered, crawler-readable show list (the app re-renders #show-list for humans).
function prerenderList(variant, shows) {
  const sep = variant === "en" ? ", " : "、";
  const li = shows.map((s) => {
    const where = [s.venue, s.city, s.country].filter(Boolean).join(sep);
    const url = (s.ticket_links && s.ticket_links[0] && s.ticket_links[0].url) || s.ticket_url || "";
    const dates = [s.start_date, s.end_date].filter(Boolean).join(" – ");
    const name = url ? `<a href="${esc(url)}" rel="nofollow">${esc(s.title)}</a>` : esc(s.title);
    return `<li>${name} — ${esc(where)}${dates ? ` (${esc(dates)})` : ""}</li>`;
  }).join("\n      ");
  return li;
}

function langSwitch(active) {
  const opt = (v, txt, lang) =>
    `<a class="lang-opt${v === active ? " active" : ""}" href="${BASE}${v}/" lang="${lang}"${v === active ? ' aria-current="true"' : ""}>${txt}</a>`;
  return `<div id="lang-switch" role="group" aria-label="Language / 語言">
        <span class="globe" aria-hidden="true">🌐</span>
        ${opt("zh-hant", "繁體中文", "zh-Hant")}
        ${opt("zh-hans", "简体中文", "zh-Hans")}
        ${opt("en", "English", "en")}
      </div>`;
}

function page(variant, shows) {
  const v = VARIANTS[variant];
  const t = variant === "en"
    ? { tagline: "Musicals playing around the world right now", theatres: "🎭 All theatres", mine: "⭐ My Musicals",
        search: "Search shows, cities, theatres…", privacy: "Privacy", terms: "Terms",
        h1: "MusicalMap — live world map of musicals playing now", listhdr: "Musicals playing now" }
    : variant === "zh-hans"
    ? { tagline: "此刻全球正在上演的音乐剧", theatres: "🎭 所有剧院", mine: "⭐ 我的音乐剧足迹",
        search: "搜寻剧名、城市、剧院…", privacy: "隐私权政策", terms: "使用条款",
        h1: "MusicalMap — 全球此刻正在上演的音乐剧即时地图", listhdr: "正在上演的音乐剧" }
    : { tagline: "此刻全球正在上演的音樂劇", theatres: "🎭 所有劇院", mine: "⭐ 我的音樂劇足跡",
        search: "搜尋劇名、城市、劇院…", privacy: "隱私權政策", terms: "使用條款",
        h1: "MusicalMap — 全球此刻正在上演的音樂劇即時地圖", listhdr: "正在上演的音樂劇" };
  // zh-hans pages load OpenCC (small t2cn dict) so i18n can simplify the UI chrome strings.
  const openccTag = variant === "zh-hans"
    ? `\n  <script src="https://cdn.jsdelivr.net/npm/opencc-js@1.3.1/dist/umd/t2cn.js"></script>` : "";
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
  <meta property="og:title" content="${esc(v.label)}" />
  <meta property="og:description" content="${esc(v.desc)}" />
  <meta property="og:url" content="${SITE}/${variant}/" />
  <meta name="twitter:card" content="summary" />
  ${jsonLd(variant, shows)}
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
  <link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.css" />
  <link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.Default.css" />
  <link rel="stylesheet" href="${BASE}css/style.css?v=${VER}" />
  <script>window.MM_VARIANT="${variant}";window.MM_BASE="${BASE}";</script>${openccTag}
</head>
<body>
  <header id="topbar">
    <a id="brand" href="${BASE}${variant}/">
      <img class="brand-logo" src="${BASE}logo.png" alt="" />
      <span class="logo">Musical<span class="logo-em">Map</span></span>
      <span class="tagline">${esc(t.tagline)}</span>
    </a>
    <nav id="topnav">
      ${langSwitch(variant)}
      <a class="nav-link" href="${BASE}theatres.html?lang=${variant}">${esc(t.theatres)}</a>
      <a id="mine-link" class="nav-cta" href="${BASE}me.html?lang=${variant}">${esc(t.mine)}</a>
    </nav>
  </header>

  <h1 class="sr-only">${esc(t.h1)}</h1>

  <div id="app">
    <aside id="sidebar">
      <div id="controls">
        <input id="search" type="search" placeholder="${esc(t.search)}" autocomplete="off" />
        <div id="tag-filters" role="group" aria-label="filter"></div>
      </div>
      <div id="count"></div>
      <!-- prerendered for crawlers (Google + AI bots that don't run JS); the app
           replaces this list on load for interactive users. -->
      <h2 class="sr-only">${esc(t.listhdr)}</h2>
      <ul id="show-list">
      ${prerenderList(variant, shows)}
      </ul>
      <footer id="foot">
        <span id="data-note"></span>
        <div class="foot-links"><a href="${BASE}privacy.html?lang=${variant}">${esc(t.privacy)}</a> · <a href="${BASE}terms.html?lang=${variant}">${esc(t.terms)}</a></div>
      </footer>
    </aside>
    <main id="map">
      <div id="timebar">
        <button id="time-play" class="tb-btn" title="play">▶</button>
        <button id="time-today" class="tb-btn tb-now" title="today">${variant === "en" ? "This month" : variant === "zh-hans" ? "本月" : "本月"}</button>
        <input id="time-range" type="range" min="0" max="36" value="0" step="1" />
        <input id="time-month" class="tb-date" type="month" />
      </div>
    </main>
  </div>

  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <script src="https://unpkg.com/leaflet.markercluster@1.5.3/dist/leaflet.markercluster.js"></script>
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
  <title>MusicalMap — live world map of musicals 全球音樂劇即時地圖</title>
  <meta name="description" content="An interactive map of musicals playing around the world right now — Broadway, West End, tours and original productions. 全球正在上演的音樂劇即時地圖。" />
  <link rel="canonical" href="${SITE}/" />
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
  const pages = ["theatres.html", "me.html", "privacy.html", "terms.html"].map(
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
