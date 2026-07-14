// Build-time generator of the tri-URL site: /en/, /zh-hans/, /zh-hant/ (+ root router,
// sitemap, robots). Run from repo root AFTER gen_variants.mjs: `node build/gen_site.mjs`.
//
// Each variant page is PRERENDERED: the show list + JSON-LD are baked into static HTML so
// Google and (JS-blind) AI crawlers see real content. The Leaflet app then hydrates on top
// for humans, reading the matching data variant. Shared js/css/data load via absolute
// root paths (custom domain serves the repo at /).
import fs from "fs";
import crypto from "crypto";
import { genPages, PAGE_SLUGS } from "./gen_pages.mjs";

const BASE = "/";
const SITE = "https://themusicalmap.com";
const VARIANTS = {
  // {NC}=國家數,build 時由資料填入(勿寫死;實測 30,舊版寫死「40+」是誇大不實,答案引擎會照抄
  // 錯誤事實。2026-07-10 改動態計算,永遠與資料一致)。
  "en":      { lang: "en",      hreflang: "en",      label: "MusicalMap — Live World Map of Musicals",
               desc: "Musicals playing around the world right now — Broadway, West End, tours and original productions across {NC} countries, updated daily." },
  "zh-hans": { lang: "zh-Hans", hreflang: "zh-Hans", label: "MusicalMap — 全球音乐剧实时地图",
               desc: "此刻全球正在上演的音乐剧实时地图：百老汇、西区、巡演与各国原创音乐剧，涵盖 {NC} 个国家，每日更新。" },
  "zh-hant": { lang: "zh-Hant", hreflang: "zh-Hant", label: "MusicalMap — 全球音樂劇即時地圖",
               desc: "此刻全球正在上演的音樂劇即時地圖：百老匯、西區、巡演與各國原創音樂劇，涵蓋 {NC} 個國家，每日更新。" },
};

// build 時從資料算真實統計,填進所有對外文案/結構化資料(勿寫死數字→會過時/誇大)。
function siteStats(shows) {
  const countries = new Set(), cities = new Set(), titles = new Set();
  for (const s of shows) { if (s.country) countries.add(s.country); if (s.city) cities.add(s.city); if (s.title) titles.add(s.title); }
  return { nCountries: countries.size, nCities: cities.size, nTitles: titles.size, nShows: shows.length };
}
function fillDesc(desc, st) { return desc.replace(/\{NC\}/g, st.nCountries); }
// build 日期(UTC,ISO):dateModified 用;CI 每日跑=每日更新,給答案引擎新鮮度訊號。
const BUILD_DATE = new Date().toISOString().slice(0, 10);
// root router(無 shows 資料)的國家數:run loop 算好真值填入,不寫死「40+」(2026-07-10)。
let ROOT_NC = 30;
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
  // 國家輪詢挑選:舊版 slice(0,300) 依資料順序(US/UK 在前)→ 中國(229)/義大利(161)等尾端國家
  // 幾乎不進 Event 結構化資料。改成各國輪流取,確保 30 國都有代表進 JSON-LD(2026-07-10 AEO)。
  // 已閉幕的場次不進結構化資料:標著 EventScheduled 的過期 event 是 Google 眼中的
  // 品質瑕疵(2026-07-14 深稽核:4 筆閉幕 ≤3 天寬限期的殘留在 JSON-LD)。rolling 長跑不看 end。
  const _t = new Date().toISOString().slice(0, 10);
  const withStart = shows.filter((s) => s.start_date && (s.end_rolling || !s.end_date || s.end_date >= _t));
  const byCountry = new Map();
  for (const s of withStart) { const k = s.country || "?"; (byCountry.get(k) || byCountry.set(k, []).get(k)).push(s); }
  const buckets = [...byCountry.values()];
  const picked = [];
  for (let r = 0; picked.length < JSONLD_CAP && buckets.some((b) => b.length > r); r++)
    for (const b of buckets) { if (r < b.length && picked.length < JSONLD_CAP) picked.push(b[r]); }
  const items = picked.map((s, i) => {
    const ticket = (s.ticket_links && s.ticket_links[0] && s.ticket_links[0].url) || s.ticket_url || undefined;
    const where = s.venue ? `${s.venue}${s.city ? ", " + s.city : ""}` : (s.city || "");
    const ev = {
      "@type": "Event", "name": s.title,
      "startDate": s.start_date, "endDate": s.end_date || undefined,
      "eventStatus": "https://schema.org/EventScheduled",
      "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
      "location": { "@type": "Place", "name": s.venue || s.city,
        "address": { "@type": "PostalAddress", "addressLocality": s.city, "addressCountry": s.country },
        // geo:資料本來就有建築級座標,放進去是 Rich Results 免費加分(2026-07-14)
        ...(typeof s.lat === "number" ? { "geo": { "@type": "GeoCoordinates", "latitude": s.lat, "longitude": s.lng } } : {}) },
      "image": s.image || undefined,
      "description": where ? `${s.title} — live stage musical at ${where}.` : `${s.title} — live stage musical.`,
      // performer/organizer:Google Event 建議欄位(缺=Rich Results 警告)。資料層沒有製作公司,
      // 用「該劇目的製作」當 PerformingGroup(業界常見做法,不虛構個人/公司名)。
      "performer": { "@type": "PerformingGroup", "name": `${s.title} company` },
      "organizer": { "@type": "Organization", "name": s.venue || s.city || "Theatre", "url": ticket || undefined },
      "offers": ticket ? { "@type": "Offer", "url": ticket, "availability": "https://schema.org/InStock", "validFrom": s.start_date } : undefined,
      "url": ticket,
    };
    return { "@type": "ListItem", "position": i + 1, "item": ev };
  });
  const st = siteStats(shows);
  const desc = fillDesc(v.desc, st);
  const app = {
    "@context": "https://schema.org", "@type": "WebApplication", "name": "MusicalMap",
    "alternateName": v.label, "url": `${SITE}/${variant}/`, "description": desc,
    "applicationCategory": "EntertainmentApplication", "operatingSystem": "Web",
    "inLanguage": v.hreflang, "isAccessibleForFree": true,
    "offers": { "@type": "Offer", "price": "0", "priceCurrency": "USD" },
  };
  const list = { "@context": "https://schema.org", "@type": "ItemList",
    "name": v.label, "numberOfItems": items.length,
    "dateModified": BUILD_DATE,   // 每日 build=每日更新,給答案引擎新鮮度訊號(2026-07-10)
    "itemListElement": items };
  // Organization + WebSite entity signals. Google/AI 一度把品牌認成既有的 "Musicmap"
  // (musicmap.info,講音樂流派史的另一站);明確宣告 name/alternateName/url/logo 幫助
  // 知識圖譜把 MusicalMap 建成獨立實體。@id 用網域錨定,三語頁指向同一實體。
  const org = { "@context": "https://schema.org", "@type": "Organization",
    "@id": `${SITE}/#organization`, "name": "MusicalMap",
    "alternateName": ["The Musical Map", "themusicalmap"],
    "url": `${SITE}/`, "logo": `${SITE}/favicon-512.png`,
    "description": `MusicalMap is a live, interactive world map of stage musicals currently playing — Broadway, West End, international tours and original productions across ${st.nCountries} countries. Not affiliated with Musicmap.` };
  const site = { "@context": "https://schema.org", "@type": "WebSite",
    "@id": `${SITE}/#website`, "name": "MusicalMap", "alternateName": v.label,
    "url": `${SITE}/`, "inLanguage": v.hreflang,
    // 站內搜尋:答案引擎/Google sitelinks searchbox 用;?q= 由 app.js 讀取預填搜尋框(2026-07-10)
    "potentialAction": { "@type": "SearchAction",
      "target": { "@type": "EntryPoint", "urlTemplate": `${SITE}/${variant}/?q={search_term_string}` },
      "query-input": "required name=search_term_string" },
    "publisher": { "@id": `${SITE}/#organization` }, "description": desc };
  // FAQPage:答案引擎(AI Overview/Perplexity)最愛引用的 Q&A 結構。答案全用 build 時真實資料算,
  // 不寫死(2026-07-10)。只在 en 頁吐英文 FAQ,zh 頁吐中文,語言一致。
  const faq = faqPage(variant, shows, st);
  return `<script type="application/ld+json">${JSON.stringify(org)}</script>\n  ` +
         `<script type="application/ld+json">${JSON.stringify(site)}</script>\n  ` +
         `<script type="application/ld+json">${JSON.stringify(app)}</script>\n  ` +
         (faq ? `<script type="application/ld+json">${JSON.stringify(faq)}</script>\n  ` : "") +
         `<script type="application/ld+json">${JSON.stringify(list)}</script>`;
}

// 從真實資料算「現在某地在演幾齣」的 FAQ(答案永遠與資料一致,不捏造)。
function faqPage(variant, shows, st) {
  const today = BUILD_DATE;
  const playingNow = (s) => (!s.start_date || s.start_date <= today) && (s.end_rolling || !s.end_date || s.end_date >= today);
  const inCity = (kw) => shows.filter(s => playingNow(s) && (s.city || "").toLowerCase().includes(kw)).length;
  const inCountry = (c) => shows.filter(s => playingNow(s) && s.country === c).length;
  const nyc = inCity("new york"), lon = inCity("london");
  const T = {
    en: [
      [`How many musicals are playing right now?`, `MusicalMap currently tracks ${st.nShows.toLocaleString()} musical productions across ${st.nCountries} countries and ${st.nCities.toLocaleString()} cities, updated daily from official sources.`],
      [`What musicals are playing on Broadway right now?`, `About ${nyc} musicals are currently playing in New York, including long-running Broadway shows like The Lion King, Wicked, Hamilton and Aladdin. See the live list on MusicalMap.`],
      [`What's playing in London's West End?`, `Around ${lon} musicals are currently playing in London, including long-runners such as The Lion King, Les Misérables, Phantom of the Opera and Wicked. MusicalMap shows exact venues, dates and official ticket links.`],
      [`Is MusicalMap free?`, `Yes. MusicalMap is completely free, has no ads, and does not sell tickets — ticket links point to official box offices or primary ticketing platforms.`],
      [`How often is the data updated?`, `The map is refreshed daily (as of ${today}) by scraping official sources: Broadway, West End, international tours, and original productions worldwide.`],
    ],
    "zh-hant": [
      [`現在全球有多少音樂劇正在上演？`, `MusicalMap 目前收錄 ${st.nShows.toLocaleString()} 個音樂劇製作，橫跨 ${st.nCountries} 個國家、${st.nCities.toLocaleString()} 座城市，每日從官方來源更新。`],
      [`現在紐約百老匯在演哪些音樂劇？`, `目前紐約約有 ${nyc} 齣音樂劇上演，包括獅子王、Wicked、漢密爾頓、阿拉丁等長跑名劇。可在 MusicalMap 看即時清單。`],
      [`倫敦西區現在在演什麼？`, `倫敦目前約有 ${lon} 齣音樂劇上演，包括獅子王、悲慘世界、歌劇魅影、Wicked 等長跑劇。MusicalMap 提供確切劇院、檔期與官方售票連結。`],
      [`MusicalMap 免費嗎？`, `是的,MusicalMap 完全免費、無廣告、不販售門票——售票連結指向官方售票處或主要票務平台。`],
      [`資料多久更新一次？`, `地圖每日更新（截至 ${today}），從官方來源抓取：百老匯、西區、國際巡演與各國原創製作。`],
    ],
    "zh-hans": [
      [`现在全球有多少音乐剧正在上演？`, `MusicalMap 目前收录 ${st.nShows.toLocaleString()} 个音乐剧制作，横跨 ${st.nCountries} 个国家、${st.nCities.toLocaleString()} 座城市，每日从官方来源更新。`],
      [`现在纽约百老汇在演哪些音乐剧？`, `目前纽约约有 ${nyc} 出音乐剧上演，包括狮子王、Wicked、汉密尔顿、阿拉丁等长跑名剧。可在 MusicalMap 看实时列表。`],
      [`伦敦西区现在在演什么？`, `伦敦目前约有 ${lon} 出音乐剧上演，包括狮子王、悲惨世界、歌剧魅影、Wicked 等长跑剧。MusicalMap 提供确切剧院、档期与官方售票链接。`],
      [`MusicalMap 免费吗？`, `是的，MusicalMap 完全免费、无广告、不贩售门票——售票链接指向官方售票处或主要票务平台。`],
      [`资料多久更新一次？`, `地图每日更新（截至 ${today}），从官方来源抓取：百老汇、西区、国际巡演与各国原创制作。`],
    ],
  };
  const qa = T[variant]; if (!qa) return null;
  return { "@context": "https://schema.org", "@type": "FAQPage",
    "mainEntity": qa.map(([q, a]) => ({ "@type": "Question", "name": q,
      "acceptedAnswer": { "@type": "Answer", "text": a } })) };
}

// Run-date label, matching the interactive app's fmtDates (js/app.js): open-ended →
// 長期上演 / Now playing; has a closing → 至 {end} / Until; future premiere → {start} 起 /
// From; else blank. Keeps the prerendered SEO list consistent with what humans see.
function runLabel(s, variant) {
  const t = new Date(); t.setHours(0, 0, 0, 0);
  const en = variant === "en";
  // en 用月名(Jul 8):數字 7/8 對美式讀者可能讀成 Aug 7;與 js/app.js fmtD 同步(2026-07-09)
  const MON = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  const f = (iso) => { const [y, m, d] = iso.split("-").map(Number);
    if (en) return y === t.getFullYear() ? `${MON[m - 1]} ${d}` : `${MON[m - 1]} ${d}, ${y}`;
    return y === t.getFullYear() ? `${m}/${d}` : `${y}/${m}/${d}`; };
  if (s.end_rolling) return en ? "Long-running" : (variant === "zh-hans" ? "长期上演" : "長期上演");
  if (s.start_date && s.end_date) return `${f(s.start_date)} – ${f(s.end_date)}`;   // 期間限定:完整起迄(與 app.js fmtDates 同步)
  if (s.end_date) return (en ? "Until " : "至 ") + f(s.end_date);
  if (s.start_date && new Date(s.start_date) > t) return en ? "From " + f(s.start_date) : f(s.start_date) + " 起";
  return "";
}
// Prerendered, crawler-readable show list (the app re-renders #show-list for humans).
// 一句可引用統計(答案引擎最愛的「headline number」)。build 時算真值,三語。
function summaryLine(variant, st) {
  const n = st.nShows.toLocaleString(), c = st.nCities.toLocaleString();
  if (variant === "en") return `MusicalMap tracks ${n} musical productions currently playing or coming in the next year across ${st.nCountries} countries and ${c} cities — Broadway, West End, international tours and original productions. Updated daily (${BUILD_DATE}). Free, no ads, does not sell tickets.`;
  if (variant === "zh-hans") return `MusicalMap 收录 ${n} 个正在上演或未来一年即将上演的音乐剧制作，横跨 ${st.nCountries} 个国家、${c} 座城市——百老汇、西区、国际巡演与各国原创。每日更新（${BUILD_DATE}）。免费、无广告、不贩售门票。`;
  return `MusicalMap 收錄 ${n} 個正在上演或未來一年即將上演的音樂劇製作，橫跨 ${st.nCountries} 個國家、${c} 座城市——百老匯、西區、國際巡演與各國原創。每日更新（${BUILD_DATE}）。免費、無廣告、不販售門票。`;
}

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
  const st = siteStats(shows);
  const desc = fillDesc(v.desc, st);   // {NC}→真實國家數(2026-07-10)
  const t = variant === "en"
    ? { tagline: "Musicals playing around the world right now", theatres: "All theatres", mine: "My Musicals", guide: "Guide",
        maphome: "Map home", search: "Search musicals, cities, theatres…", privacy: "Privacy", terms: "Terms",
        h1: "MusicalMap — Live World Map of Musicals Playing Now", listhdr: "Musicals playing now and in the coming year", filterLabel: "Category" }
    : variant === "zh-hans"
    ? { tagline: "此刻全球正在上演的音乐剧", theatres: "所有剧院", mine: "我的音乐剧", guide: "怎么使用",
        maphome: "地图首页", search: "搜寻音乐剧名、城市、剧院…", privacy: "隐私政策", terms: "使用条款",
        h1: "MusicalMap — 全球此刻正在上演的音乐剧实时地图", listhdr: "正在上演与未来一年的音乐剧", filterLabel: "分类" }
    : { tagline: "此刻全球正在上演的音樂劇", theatres: "所有劇院", mine: "我的音樂劇", guide: "怎麼使用",
        maphome: "地圖首頁", search: "搜尋音樂劇名、城市、劇院…", privacy: "隱私權政策", terms: "使用條款",
        h1: "MusicalMap — 全球此刻正在上演的音樂劇即時地圖", listhdr: "正在上演與未來一年的音樂劇", filterLabel: "分類" };
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
  <meta name="description" content="${esc(desc)}" />
  <link rel="canonical" href="${SITE}/${variant}/" />
  ${hreflangLinks()}
  <meta property="og:type" content="website" />
  <meta property="og:site_name" content="MusicalMap" />
  <meta property="og:title" content="${esc(v.label)}" />
  <meta property="og:description" content="${esc(desc)}" />
  <meta property="og:url" content="${SITE}/${variant}/" />
  <meta property="og:image" content="${SITE}/og-image.png" />
  <meta property="og:image:width" content="1200" />
  <meta property="og:image:height" content="630" />
  <meta property="og:image:alt" content="MusicalMap — Live World Map of Musicals" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="${esc(v.label)}" />
  <meta name="twitter:description" content="${esc(desc)}" />
  <meta name="twitter:image" content="${SITE}/og-image.png" />
  <!-- favicon: Google 只收正方形且 ≥48px 的圖示;SVG 必須用 favicon.svg(2244×2244 方形置中版),logo.svg 是 1245×2244 直式會被拒→退回地球圖示 -->
  <link rel="icon" href="${BASE}favicon.ico?v=3" sizes="any" />
  <link rel="icon" type="image/svg+xml" href="${BASE}favicon.svg" />
  <link rel="icon" type="image/png" sizes="96x96" href="${BASE}favicon-96.png?v=3" />
  <link rel="icon" type="image/png" sizes="192x192" href="${BASE}favicon-192.png?v=3" />
  <link rel="apple-touch-icon" href="${BASE}apple-touch-icon.png?v=3" />
  ${jsonLd(variant, shows)}
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <!-- LCP 關鍵路徑預熱:Leaflet CSS/JS 從 unpkg、地圖圖磚從 mapbox(2026-07-10 效能)。未預連=首屏前
       多付一次 DNS+TCP+TLS 握手(~100-300ms)。preload 資料檔=與腳本並行下載,省 LCP。 -->
  <link rel="preconnect" href="https://unpkg.com" crossorigin />
  <link rel="preconnect" href="https://api.mapbox.com" crossorigin />
  <link rel="preload" as="fetch" type="application/json" crossorigin href="${BASE}data/variants/shows.${variant}.json?v=${VER}" />
  <link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,900&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" integrity="sha384-sHL9NAb7lN7rfvG5lfHpm643Xkcjzp4jFvuavGOndn6pjVqS6ny56CAt3nsEVT4H" crossorigin="anonymous" />
  <link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.css" integrity="sha384-pmjIAcz2bAn0xukfxADbZIb3t8oRT9Sv0rvO+BR5Csr6Dhqq+nZs59P0pPKQJkEV" crossorigin="anonymous" />
  <link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.Default.css" integrity="sha384-wgw+aLYNQ7dlhK47ZPK7FRACiq7ROZwgFNg0m04avm4CaXS+Z9Y7nMu8yNjBKYC+" crossorigin="anonymous" />
  <link rel="stylesheet" href="${BASE}css/style.css?v=${VER}" />
  <script>window.MM_VARIANT="${variant}";window.MM_BASE="${BASE}";window.MM_DATA_VER="${VER}";</script>${openccTag}
  <script src="${BASE}js/mm-acct-menu.js?v=${VER}" defer></script>
  <script src="${BASE}js/mm-xlang.js?v=1" defer></script><!-- 跨網域語言傳遞 --><!-- 登入過(mm_owner cookie)→「我的音樂劇」CTA 自動換成大頭照選單;未登入照常顯示 CTA -->
  <script src="${BASE}js/mm-lang.js?v=${VER}" defer></script><!-- 語言切換下拉(globe→繁中/简中/English)開關行為 -->

  <!-- Google Analytics(GA4 G-GC07MYC1MY;訪客來源/行為分析。root 路由頁不埋(立即轉走);隱私揭露見 privacy.html §1/§3) -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-GC07MYC1MY"></script>
  <script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','G-GC07MYC1MY');</script>
  <!-- Cloudflare Web Analytics(手動 JS snippet,2026-07-13:WA「自動注入」在本 zone 從未生效
       →Page views 一直 0;dashboard 已切「Enable with JS Snippet installation」。token=5953964f…
       (WA 站的 beacon token,≠管理網址那串 site id f5debd92…,拿錯顆收不到資料) -->
  <script type='module' src='https://static.cloudflareinsights.com/beacon.min.js' data-cf-beacon='{"token": "5953964f9c434c67bcc12dd3eaedf340"}'></script>
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
      <a class="nav-link" href="${BASE}${variant}/guide">${esc(t.guide)}</a><!-- 直連同語言靜態變體(v2.15.0 起),不繞 ?hl= 路由;theatres 已撤站(v2.18.0) -->
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
      <!-- 可引用統計句(JS-blind 爬蟲/答案引擎;#count 是 JS 填的,爬蟲看不到數字)。build 時算真值。 -->
      <p class="sr-only" id="mm-summary">${esc(summaryLine(variant, st))}</p>
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
  <link rel="icon" type="image/svg+xml" href="${BASE}favicon.svg" />
  <link rel="icon" type="image/png" sizes="96x96" href="${BASE}favicon-96.png?v=3" />
  <link rel="apple-touch-icon" href="${BASE}apple-touch-icon.png?v=3" />
  <meta property="og:type" content="website" />
  <meta property="og:site_name" content="MusicalMap" />
  <meta property="og:title" content="MusicalMap — Live World Map of Musicals" />
  <meta property="og:description" content="Musicals playing around the world right now — Broadway, West End, tours and original productions across ${ROOT_NC} countries." />
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
  <!-- ⚠️ 正式站上這頁幾乎不會被看到:root 的語言分流已改在 Cloudflare Redirect Rules
       (zone themusicalmap.com → Rules → root-lang-redirect-{zh-hant,zh-hans,en-default},
       按 Accept-Language 302,2026-07-13 設定)。原因:這頁的 JS 變身讓 Googlebot 把
       root 渲染成 /en/ 同內容 → /en/ 被判重複頁不收錄(GSC 實查)。下方 JS 僅作
       CF 規則失效時的 fallback;動語言判斷邏輯時兩處要一起改。 -->
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
  // 三語地圖根頁每日重建(劇目進出)→ lastmod=build 日期,給 Google 每日重爬訊號(2026-07-10)。
  const variants = ["en", "zh-hans", "zh-hant"].map((v) =>
    `  <url><loc>${SITE}/${v}/</loc><lastmod>${BUILD_DATE}</lastmod><changefreq>daily</changefreq>` +
    `<xhtml:link rel="alternate" hreflang="en" href="${SITE}/en/"/>` +
    `<xhtml:link rel="alternate" hreflang="zh-Hans" href="${SITE}/zh-hans/"/>` +
    `<xhtml:link rel="alternate" hreflang="zh-Hant" href="${SITE}/zh-hant/"/>` +
    `<xhtml:link rel="alternate" hreflang="x-default" href="${SITE}/"/></url>`);
  // …plus the standalone pages (kept from the previous sitemap so they stay indexed).
  // me.html 刻意不列:登入閘頁(爬蟲只看到「載入中」),head 已加 noindex;公開內容在 u.html。
  // theatres.html 已撤站(2026-07-09 使用者指示,v2.18.0):檔案刪除→404,sitemap 不再列。
  // 無副檔名 canonical:GH Pages 與 Cloudflare Pages 皆直達 200(CF 對 .html 形式會 308 到無副檔名)。
  // about/guide/privacy/terms 已拆三語靜態變體(gen_pages.mjs):列變體網址+hreflang 叢集,根網址=x-default 路由。
  const pageCluster = (p) => ["en", "zh-hans", "zh-hant"].map((v) =>
    `  <url><loc>${SITE}/${v}/${p}</loc><lastmod>${BUILD_DATE}</lastmod>` +
    `<xhtml:link rel="alternate" hreflang="en" href="${SITE}/en/${p}"/>` +
    `<xhtml:link rel="alternate" hreflang="zh-Hans" href="${SITE}/zh-hans/${p}"/>` +
    `<xhtml:link rel="alternate" hreflang="zh-Hant" href="${SITE}/zh-hant/${p}"/>` +
    `<xhtml:link rel="alternate" hreflang="x-default" href="${SITE}/${p}"/></url>`);
  const pages = PAGE_SLUGS.flatMap(pageCluster);
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
  // /build/ = 頁面 source 模板(build/pages/*.html),部署會帶出去但不該被收錄(與變體頁重複內容)。
  // 每個 UA 群組都要各自 Disallow:爬蟲匹配到具名群組後會忽略 * 群組的規則。
  return "# MusicalMap — open to all crawlers, including AI/answer engines.\n" +
         "User-agent: *\nAllow: /\nDisallow: /build/\n\n" +
         bots.map((b) => `User-agent: ${b}\nAllow: /\nDisallow: /build/`).join("\n\n") +
         `\n\nSitemap: ${SITE}/sitemap.xml\n`;
}

// ---- run ----
for (const variant of Object.keys(VARIANTS)) {
  const shows = JSON.parse(fs.readFileSync(`data/variants/shows.${variant}.json`, "utf8")).shows;
  ROOT_NC = siteStats(shows).nCountries;   // 真實國家數,給 rootRouter og 用(勿寫死 40+)
  fs.mkdirSync(variant, { recursive: true });
  fs.writeFileSync(`${variant}/index.html`, page(variant, shows));
  console.log(`${variant.padEnd(8)} → ${variant}/index.html (${shows.length} shows, ${Math.min(shows.length, JSONLD_CAP)} in JSON-LD)`);
}
fs.writeFileSync("index.html", rootRouter());
genPages();
fs.writeFileSync("sitemap.xml", sitemap());
fs.writeFileSync("robots.txt", robots());
console.log("root index.html (router) + sitemap.xml + robots.txt written");
