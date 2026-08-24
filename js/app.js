/* MusicalMap — frontend
 * Reads data/shows.json and renders an interactive map + synced sidebar.
 * Data layer (scrapers) and presentation layer (this file) are decoupled.
 *
 * Security: show data is UNTRUSTED (comes from scrapers). All text is escaped
 * via esc(); ticket + image URLs are protocol-whitelisted.
 */

const TODAY = new Date();
const TODAY0 = (() => { const d = new Date(); d.setHours(0, 0, 0, 0); return d; })();
const CUR_Y = TODAY0.getFullYear(), CUR_M = TODAY0.getMonth();
let MAX_MONTHS = 12;                          // slider range = 1 year ahead, auto-rolling (recomputeRange pins it to 12)
let MIN_MONTHS = 0;                           // most-negative offset (into the PAST); set from archive index
// Past browsing is built end-to-end (archive index + lazy year loads) but kept OFF
// for now — the archive keeps accumulating server-side; flip to true to surface it.
const SHOW_HISTORY = false;
let monthOffset = 0;                          // 0 = current month; the map shows this whole month
// new Date(y, m, 1) auto-normalizes overflowing months, so offset arithmetic is safe.
const monthStart = () => new Date(CUR_Y, CUR_M + monthOffset, 1);
const monthEnd = () => new Date(CUR_Y, CUR_M + monthOffset + 1, 0, 23, 59, 59, 999);
const selYM = () => { const d = monthStart(); return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`; };
const isThisMonth = () => monthOffset === 0;

// ---------- safety helpers (untrusted scraped data) ----------
function esc(v) {
  return String(v ?? "")
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;").replace(/'/g, "&#39;");
}
// Search normaliser: lowercase, strip accents (é→e), drop apostrophes, and turn
// every other punctuation (hyphens, !, &, …) into spaces, so "notre dame",
// "Notre-Dame", "les mise", "mamma mia!" all match regardless of accent/punctuation.
// CJK/Hangul/Kana are preserved so 悲慘世界 still matches.
const fold = (s) => (s || "").toLowerCase().normalize("NFKD")
  .replace(/[̀-ͯ]/g, "")                 // strip combining accents
  .replace(/&/g, " and ")                 // & → and:「&」原被當標點丟掉,搜「&」找不到 & Juliet (2026-07-17)
  .replace(/['’ʼ]/g, "")                  // drop apostrophes (kiki's → kikis)
  .replace(/臺/g, "台")                    // 異體字: 臺北/臺灣 ⇄ 台北/台灣 (search both forms)
  .replace(/[・･]/g, "")                    // 日文中黑點:レ・ミゼラブル ⇄ レミゼラブル 都搜得到 (2026-07-10)
  .replace(/[^a-z0-9　-鿿가-힯]+/g, " ")  // other punctuation → space
  .replace(/\s+/g, " ").trim();

function safeUrl(u) {
  if (!u) return null;
  try {
    const p = new URL(u, location.href);
    return ["http:", "https:"].includes(p.protocol) ? p.href : null;
  } catch { return null; }
}

// ── Affiliate / commission links ────────────────────────────────────────────
// Data keeps CLEAN canonical URLs (e.g. Ticketmaster attraction pages); monetised
// wrapping is applied HERE, in one place, at click/render time — so you can add or
// change a commission program WITHOUT re-scraping, and the data stays portable.
// To enable: sign up for each program, then uncomment its line and paste YOUR IDs.
// Deep-linking is supported by all of these — wrapping a clean attraction/main page
// URL is enough to earn commission (the click sets a cookie; the buyer is tracked
// through to checkout). Formats below are the real ones for each affiliate network
// (2026 research). The map's outbound domains that HAVE a program:
//   • ticketmaster.* ............ Impact (impact.com) — apply at app.impact.com
//   • atgtickets.com ............ Partnerize
//   • londontheatre.co.uk ....... TodayTix Group, via Impact (~1-2%; NOT ATG/Awin — verified)
//   • stage-entertainment.de .... German networks (~4-7%)
// (Korea/Hungary/Taiwan/Japan official sources have no public program → passthrough.)
// Multi-network affiliate wrapping — config in MM_CONFIG.AFFILIATE (js/config.js).
// One place, at render time: data stays raw, changing an ID is a config edit, never a
// re-scrape. Each program is independent and DORMANT until its creds are filled.
const AFF = (window.MM_CONFIG || {}).AFFILIATE || {};
const AFF_SUBID = (window.MM_CONFIG || {}).AFFILIATE_SUBID || "";
// already-a-tracking-link hosts (never double-wrap)
const AFF_TRACKING = /(?:\.evyy\.net|\.pxf\.io|\.sjv\.io|prf\.hn|\.awin1\.com|viglink\.com|sovrn\.co)$/i;
function affReady(c) {
  if (!c) return false;
  if (c.net === "impact") return !!(c.domain && c.ids);
  if (c.net === "partnerize") return !!c.camref;
  if (c.net === "awin") return !!(c.mid && c.affid);
  if (c.net === "tmpl") return !!(c.tmpl && c.tmpl.includes("{url}"));
  return false;
}
function affWrap(c, u) {
  const e = encodeURIComponent(u);
  if (c.net === "impact") return `https://${c.domain}/c/${c.ids}?u=${e}` + (AFF_SUBID ? `&subId1=${encodeURIComponent(AFF_SUBID)}` : "");
  if (c.net === "partnerize") return `https://prf.hn/click/camref:${c.camref}/destination:${e}`;
  if (c.net === "awin") return `https://www.awin1.com/cread.php?awinmid=${c.mid}&awinaffid=${c.affid}&ued=${e}`;
  if (c.net === "tmpl") return c.tmpl.replace("{url}", e);   // network's own deep-link template
  return u;
}
function affiliateUrl(u) {
  if (!u) return u;
  try {
    const host = new URL(u).hostname;
    if (AFF_TRACKING.test(host)) return u;                 // already a tracking link
    for (const key in AFF) {
      if (host.includes(key) && affReady(AFF[key])) return affWrap(AFF[key], u);
    }
  } catch { /* leave as-is */ }
  return u;   // passthrough — no (ready) program for this domain
}

// CDN-side thumbnailing: request a small CROPPED square-ish poster for markers
// and list thumbnails. Contentful / imgix / craft.cloud take different params.
// Original full-size images everywhere — no CDN downscaling/compression.
// (User preference: image quality over load speed.)
// CSS-safe URL for `background-image:url('…')`. esc() (HTML-encoding) is WRONG in
// CSS context — an apostrophe becomes &#39; which CSS does NOT decode, breaking the
// URL (e.g. "Everybody's Talking About Jamie" poster showed in the popup <img> but
// not in the marker/sidebar background-image). Percent-encode the chars that would
// break url('…') instead.
const cssUrl = (u) => (u || "").replace(/['"()\s\\]/g,
  (c) => "%" + c.charCodeAt(0).toString(16).padStart(2, "0"));
function thumb(url) {
  return safeUrl(url);   // markers stay small — the source thumbnail is fine at 140px
}
function posterFull(url) {
  const u = safeUrl(url);
  if (!u) return u;
  // jegy.hu stores a tiny "{slug}-{W}-{H}-{id}.jpg" thumbnail (e.g. 222×131); the big popup
  // poster upscales it into a blur. Swap to the full-res "-original-" variant for the popup.
  if (u.includes("jegy.hu/")) {
    return u.replace(/-\d+-\d+-(\d+\.(?:jpe?g|png|webp))$/i, "-original-$1");
  }
  return u;
}

// ---------- "is this show playing during the selected month?" ----------
// A show counts if its run [start, end] overlaps the month at all — i.e. the run
// crosses into the month even by a single day (user's rule). Missing start/end
// is treated as open-ended (long-runners with no announced close stay visible).
// Open-ended long-runners (Broadway/West End residents) carry no end_date — their
// closing isn't announced, only a rolling booking window. Treating "no end" as
// "runs forever" wrongly kept them on the map years out (e.g. Buena Vista Social
// Club, booked through Jan 2027, still showing at 2029). Cap them at a ~1yr booking
// horizon from today; shows WITH a real end_date (tours) are unaffected.
const OPEN_RUN_HORIZON = 12;  // months ahead an open-ended run is assumed to still play
// 'YYYY-MM-DD' → 本地午夜 Date。直接 new Date('2026-04-01') 會解析成 UTC 午夜,美洲時區(UTC-)
// 會變成前一天晚上 → 選月份時多顯示/漏顯示邊界一天的劇(2026-07-10 實測紐約:4/1 開演劇誤入 3 月)。
function localDate(s) { if (!s) return null; const [y, m, d] = String(s).slice(0, 10).split("-").map(Number); return (y && m) ? new Date(y, m - 1, d || 1) : null; }
function overlapsMonth(show) {
  const ms = monthStart(), me = monthEnd();
  const start = localDate(show.start_date);
  // end_rolling 劇卡片顯示「長期上演」(fmtDates 忽略 end_date);地圖判定也必須忽略 end_date、當開放式
  // 走 horizon,否則旗艦定目劇(紅磨坊/Ragtime/Titanique)拖過 end_date 當月就從地圖消失、與標籤矛盾(2026-07-10)。
  const end = show.end_rolling ? null : localDate(show.end_date);
  if (start && start > me) return false;   // run begins after this month
  if (end) {
    if (end < ms) return false;            // run ended before this month
    // 演完隔天就撤(2026-07-13 使用者指示):看「當前月」時,已結束的場次不再顯示——
    // 站的招牌是「此刻正在上演」,演完還掛著=名不符實(Lexington 7/12 場 7/13 仍在圖上)。
    // 用「觀看者本地今天」比對:台北 7/13 看不到 7/12 結束的劇;美國觀眾當地 7/12(末場
    // 開演前)仍看得到——時區各自正確。過去月份由 archive 服務,未來月不受影響。
    if (isThisMonth() && end < TODAY0) return false;
  } else if (!start) {
    // 起迄日期一個都沒有(來源只說「有在賣」)。落到下面的 horizon 判斷會等於宣稱
    // 「未來一整年每個月都在演」——2026-08-12 線上實測:4 筆(Lion King 馬德里、
    // MJ 斯海弗寧恩、El Alma al aire、博物馆奇遇记)在時間軸 13 個月全部出現,
    // 日期欄還是空白。既然無從得知未來檔期,就只在「當前月」出現:
    // 來源列著在售 → 現在有演是合理推論;未來月份不知道 → 不聲稱。
    return isThisMonth();
  } else {
    const horizon = new Date(CUR_Y, CUR_M + OPEN_RUN_HORIZON + 1, 0, 23, 59, 59, 999);
    if (ms > horizon) return false;        // open-ended: don't claim a run past the booking horizon
  }
  return true;                             // any overlap → show on the map
}

// ---------- Map ----------
const map = L.map("map", {
  zoomControl: true,
  worldCopyJump: true,
  maxBoundsViscosity: 1.0,            // hard stop at the vertical edges (no grey strips)
}).setView([42, -40], 3);
window.mmMap = map;   // 給截圖/測試腳本設定視角用(guide 素材產製)
// Never show the grey backdrop above/below the world: the world must always cover the
// full viewport height. (1) minZoom is raised so 256·2^z ≥ box height — you can't zoom
// out into grey; (2) maxBounds clamps latitude to the world while leaving longitude
// effectively unbounded (Infinity) so horizontal wrap/scroll still works.
function fillViewportHeight() {
  const h = map.getSize().y;
  const minZ = Math.ceil(Math.log2(Math.max(1, h) / 256));
  if (map.getMinZoom() !== minZ) map.setMinZoom(minZ);
  if (map.getZoom() < minZ) map.setZoom(minZ);
}
map.setMaxBounds([[-85, -Infinity], [85, Infinity]]);
fillViewportHeight();
map.on("resize", fillViewportHeight);
// 桌面開卡「舒適區」定位校正(2026-07-14,取代 popup autoPan):卡片超出
// 「地圖頂 +24px ~ 時間軸 bar 上緣 -16px」時,量實際卡高把卡片垂直置中於該區、
// 橫向拉回可視範圍。所有開卡路徑(點 marker/側欄/低倍飛入)共用;
// 手機是底部 sheet 不適用。搭配 focusShow 的「低倍先飛 zoom 12」,
// 修掉最小 zoom 開卡時卡片超出地圖頂又無縱向空間可拖的卡死。
map.on("popupopen", (e) => {
  if (window.matchMedia("(max-width: 680px)").matches) return;
  const el = e.popup.getElement();
  if (!el) return;
  const settle = () => {
    if (!el.isConnected) return;   // 校正前卡片已被關掉
    const mapR = document.getElementById("map").getBoundingClientRect();
    const tb = document.getElementById("timebar");
    const barTop = tb ? tb.getBoundingClientRect().top : mapR.bottom;
    const r = el.getBoundingClientRect();
    const top = mapR.top + 24;
    const bot = barTop - 16;
    // 內容整體=卡片+其下方的海報 marker(icon 高 72,錨在卡片正下方)——marker 不算進去
    // 會被置中結果壓到時間軸 bar 上(2026-07-14 使用者抓到 Moncton 案)。
    const MARKER_BELOW = 76;
    const cTop = r.top;
    const cBot = r.bottom + MARKER_BELOW;
    let dx = 0;
    let dy = 0;
    if (cTop < top || cBot > bot) {
      dy = (cBot - cTop > bot - top)
        ? cTop - top                                 // 內容比舒適區還高:保頂對齊,至少標題可見
        : (cTop + cBot) / 2 - (top + bot) / 2;       // 卡片+marker 整體垂直置中於舒適區
    }
    if (r.left < mapR.left + 12) dx = r.left - (mapR.left + 12);
    else if (r.right > mapR.right - 12) dx = r.right - (mapR.right - 12);
    if (dx || dy) map.panBy([dx, dy], { animate: true });
  };
  requestAnimationFrame(settle);
  // 海報圖載入完成後卡高會長高,再校一次(仍超出舒適區才會動)
  el.querySelectorAll("img").forEach((im) => {
    if (!im.complete) im.addEventListener("load", () => requestAnimationFrame(settle), { once: true });
  });
});
// Base layers: light street map (default) + satellite imagery, toggle top-right.
// Mapbox Streets basemap (green land / blue water — the clean look). Token is public
// (see js/config.js). @2x/512 tiles with zoomOffset -1 give crisp retina rendering.
const MAPBOX_TOKEN = (window.MM_CONFIG && window.MM_CONFIG.MAPBOX_TOKEN) || "";
const streets = L.tileLayer(
  `https://api.mapbox.com/styles/v1/mapbox/streets-v12/tiles/512/{z}/{x}/{y}@2x?access_token=${MAPBOX_TOKEN}`, {
  attribution: '&copy; <a href="https://www.mapbox.com/about/maps/">Mapbox</a> &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
  tileSize: 512, zoomOffset: -1, maxZoom: 19,
}).addTo(map);
const satellite = L.tileLayer(
  "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}", {
    attribution: "Tiles &copy; Esri, Maxar, Earthstar Geographics", maxZoom: 19,
  });
L.control.layers({ [t("map")]: streets, [t("satellite")]: satellite }, null, { position: "topright" }).addTo(map);

// ── 定位「附近的音樂劇」(2026-08-24 使用者需求:根據我所在位置顯示附近有什麼)──
// 點定位鈕→取瀏覽器 GPS→標「你的位置」+飛過去(zoom 9,附近 marker 可見)+側欄改成「依距離排序」。
// 距離用 haversine(球面);再點「清除定位」回到正常分類清單。權限拒絕/無 GPS→非阻斷式提示。
var USER_POS = null, NEARBY = false, userMarker = null;
function haversineKm(a, b) {
  const R = 6371, r = Math.PI / 180;
  const dLat = (b.lat - a.lat) * r, dLng = (b.lng - a.lng) * r;
  const h = Math.sin(dLat / 2) ** 2 +
    Math.cos(a.lat * r) * Math.cos(b.lat * r) * Math.sin(dLng / 2) ** 2;
  return 2 * R * Math.asin(Math.sqrt(h));
}
function locateToast(msg) {
  let el = document.getElementById("mm-toast");
  if (!el) { el = document.createElement("div"); el.id = "mm-toast"; document.body.appendChild(el); }
  el.textContent = msg; el.classList.add("show");
  clearTimeout(locateToast._t);
  locateToast._t = setTimeout(() => el.classList.remove("show"), 4200);
}
function clearNearby() {
  NEARBY = false;
  if (userMarker) { map.removeLayer(userMarker); userMarker = null; }
  render();
}
function doLocate() {
  const btn = document.querySelector(".mm-locate");
  if (!navigator.geolocation) { locateToast(t("locate_denied")); return; }
  if (btn) btn.classList.add("loading");
  navigator.geolocation.getCurrentPosition(
    (pos) => {
      if (btn) btn.classList.remove("loading");
      USER_POS = { lat: pos.coords.latitude, lng: pos.coords.longitude };
      NEARBY = true;
      if (userMarker) map.removeLayer(userMarker);
      userMarker = L.circleMarker([USER_POS.lat, USER_POS.lng],
        { radius: 8, weight: 3, color: "#fff", fillColor: "#1f7a8c", fillOpacity: 1, className: "mm-userpin" })
        .addTo(map).bindTooltip(t("you_are_here"), { direction: "top" });
      map.flyTo([USER_POS.lat, USER_POS.lng], 9, { animate: true, duration: 1.2 });
      render();
      if (els && els.list) els.list.scrollTop = 0;
    },
    () => { if (btn) btn.classList.remove("loading"); locateToast(t("locate_denied")); },
    { enableHighAccuracy: false, timeout: 10000, maximumAge: 300000 });
}
const LocateControl = L.Control.extend({
  options: { position: "bottomleft" },
  onAdd() {
    const b = L.DomUtil.create("button", "mm-locate");
    b.type = "button"; b.title = t("locate"); b.setAttribute("aria-label", t("locate"));
    // 準星圖示(定位慣用符號)
    b.innerHTML = '<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true">'
      + '<circle cx="12" cy="12" r="4" fill="none" stroke="currentColor" stroke-width="2"/>'
      + '<line x1="12" y1="1" x2="12" y2="5" stroke="currentColor" stroke-width="2"/>'
      + '<line x1="12" y1="19" x2="12" y2="23" stroke="currentColor" stroke-width="2"/>'
      + '<line x1="1" y1="12" x2="5" y2="12" stroke="currentColor" stroke-width="2"/>'
      + '<line x1="19" y1="12" x2="23" y2="12" stroke="currentColor" stroke-width="2"/></svg>';
    L.DomEvent.disableClickPropagation(b);
    L.DomEvent.on(b, "click", (e) => { L.DomEvent.stop(e); doLocate(); });
    return b;
  },
});
map.addControl(new LocateControl());
// 法務連結放 attribution 列(Google Maps 慣例:全螢幕地圖 app 無頁尾,隱私/條款跟圖資出處同列);
// 頂部 nav 留給功能項,手機版也因此看得到法務連結(nav-link 在手機被藏)
// 法務連結包一層 .attr-legal:手機用 CSS 隱藏(改由 header 的 ≡ 選單提供,因 attribution
// 在手機會被 Safari 底部工具列蓋住、點不到);桌面照舊顯示。© 品牌識別保留不藏。
map.attributionControl.addAttribution(
  `© ${new Date().getFullYear()} MusicalMap` +   // 短版版權(法律上非必要但具專業識別;不用過時的 All Rights Reserved)
  `<span class="attr-legal"> · ` +
  `<a href="${window.MM_BASE || "/"}about?hl=${window.MM_VARIANT || "zh-hant"}">${t("about_short")}</a> · ` +
  `<a href="${window.MM_BASE || "/"}privacy?hl=${window.MM_VARIANT || "zh-hant"}">${t("privacy_short")}</a> · ` +
  `<a href="${window.MM_BASE || "/"}terms?hl=${window.MM_VARIANT || "zh-hant"}">${t("terms_short")}</a> · ` +
  // 信箱印全文(不寫成「聯絡」二字):廣告/合作洽談方與媒體採購常直接掃頁面上的 @ 字串或 mailto: href,
  // 只給一個 label 連結等於沒露出。語言中性,三語變體共用同一串,不進字典。
  `<a href="mailto:contact@themusicalmap.com">contact@themusicalmap.com</a></span>`);

// (移除:開發用的縮放層級讀數「z 2」原本露在 +/- 下方給使用者看——dev 殘留,破壞精品感,2026-07-10)
const cluster = L.markerClusterGroup({
  maxClusterRadius: 90,
  spiderfyOnMaxZoom: true,
  showCoverageOnHover: false,
  // size the bubble by how many shows it holds. Radius ∝ √n so the *area* tracks
  // the count and big clusters stay visibly bigger (linear scaling saturated at
  // the cap, making 39/83/109 look identical — user feedback).
  iconCreateFunction: (c) => {
    const n = c.getChildCount();
    const size = Math.round(Math.max(30, Math.min(112, 20 + Math.sqrt(n) * 8.5)));
    const fs = Math.round(Math.max(12, size * 0.36));
    return L.divIcon({
      html: `<div class="mm-cluster" style="width:${size}px;height:${size}px;font-size:${fs}px"><span>${n}</span></div>`,
      className: "mm-cluster-wrap",
      iconSize: [size, size],
    });
  },
});
map.addLayer(cluster);

// 手機:把開啟的 popup 移到 <body>,讓 CSS 的底部 sheet(position:fixed)生效——
// Leaflet 的 popup pane 有 transform,fixed 會相對 pane 而非畫面,貼不到底(2026-07-04 使用者回報「圖卡」修正)。
// 關閉時元素連同事件由 Leaflet 移除;移到 body 後 el.remove() 仍正常清掉。
const _isPhone = () => window.matchMedia("(max-width: 680px)").matches;
map.on("popupopen", (e) => {
  if (!_isPhone()) return;
  const el = e.popup.getElement();
  if (el && el.parentElement !== document.body) document.body.appendChild(el);
});

// Cluster bubbles don't support riseOnHover (that's marker-only); on hover, raise the
// bubble above its neighbours so an obscured circle pops fully into view (CSS then grows
// it slightly, like the poster cards). Reset on mouse-out.
cluster.on("clustermouseover", (e) => (e.propagatedFrom || e.layer).setZIndexOffset(10000));
cluster.on("clustermouseout",  (e) => (e.propagatedFrom || e.layer).setZIndexOffset(0));

// Several productions can share one venue's exact coordinate (e.g. three shows at
// 臺中國家歌劇院). Spread each such group around a tiny ring (~38 m) so they cluster
// when zoomed out (the world map still wants counts) but break apart by pixel
// distance as you zoom in — and end up clearly separated rather than permanently
// stacked behind one another. Real lat/lng stay on the show; we draw at dlat/dlng.
function spreadSame(list) {
  const g = {};
  list.forEach((s) => {
    s.dlat = s.lat; s.dlng = s.lng;
    if (typeof s.lat !== "number" || typeof s.lng !== "number") return;
    const k = s.lat.toFixed(5) + "," + s.lng.toFixed(5);
    (g[k] = g[k] || []).push(s);
  });
  Object.values(g).forEach((grp) => {
    if (grp.length < 2) return;
    const R = 0.00034, latr = grp[0].lat * Math.PI / 180;  // ~38 m ring
    grp.forEach((s, i) => {
      const a = 2 * Math.PI * i / grp.length - Math.PI / 2;
      s.dlat = s.lat + R * Math.sin(a);
      s.dlng = s.lng + R * Math.cos(a) / Math.cos(latr);
    });
  });
}

// ---------- State ----------
let ALL = [];                                 // live snapshot (current + future) from shows.json
const SYN = {};                               // group → 劇情簡介(繁中);runtime 載入,見 boot()
let LOAD_FAILED = false;                      // shows.json 載入失敗 → 空狀態顯示錯誤而非「0 部音樂劇」
let ARCH = {};                                // year -> historical runs (lazy-loaded from data/archive/<year>.json)
let ARCH_INDEX = null;                        // data/archive/index.json (which years exist)
const archLoading = {};                       // year -> in-flight fetch promise (dedup)
let markerById = {};
let didFitBounds = false;
let DATA_UPDATED = "";   // shows.json meta.generated_at, for the footer note (re-rendered on lang change)

function renderDataNote() {
  if (!els.note) return;   // #data-note removed from layout (sources shown elsewhere)
  const u = DATA_UPDATED ? t("updated", { d: DATA_UPDATED }) : "";
  els.note.textContent = t("sources", { u });
}

// 語言切換的重繪統一由檔尾單一 mm-langchange listener 處理(需先捕捉開啟中的卡再重建,
// 兩個 listener 會互相搶跑導致卡被 clearLayers 關掉,故此處不再單獨掛)。

const els = {
  list: document.getElementById("show-list"),
  count: document.getElementById("count"),
  search: document.getElementById("search"),
  tagFilters: document.getElementById("tag-filters"),
  note: document.getElementById("data-note"),
  tRange: document.getElementById("time-range"),
  tMonth: document.getElementById("time-month"),
  tPlay: document.getElementById("time-play"),
  tToday: document.getElementById("time-today"),
};

// Tradition/origin tags (must match build_shows.py classify_tag output). Order =
// display order; colour = the pill accent. ACTIVE_TAGS empty == no filter (all).
const TAG_DEFS = [
  ["Broadway/West End", "Broadway/West End", "#c79a3b"],
  ["德奧音樂劇", "德奧音樂劇", "#b4232a"],
  ["法式音樂劇", "法式音樂劇", "#1d4ed8"],
  ["西葡音樂劇", "西葡音樂劇", "#ea580c"],
  ["中國原創", "中國原創", "#dc2626"],
  ["台灣原創", "台灣原創", "#0f766e"],
  ["日本原創", "日本原創", "#db2777"],
  ["韓國原創", "韓國原創", "#7c3aed"],
  ["歐陸原創", "歐陸原創", "#0891b2"],
];
const ACTIVE_TAGS = new Set();   // empty = show every tradition
const TAG_COLOR = Object.fromEntries(TAG_DEFS.map(([t, , c]) => [t, c]));
const tagLabel = (tag) => t("tag_" + tag);
const tagBadge = (tag) => tag
  ? `<span class="tag-badge" style="--tag-color:${TAG_COLOR[tag] || "#64748b"}">${esc(tagLabel(tag))}</span>`
  : "";

const tagCountSpans = {};   // tag -> the chip's count <span>, updated per month

function buildTagFilters() {
  // The PILL SET is stable (built from every tradition that ever appears), so pills
  // don't pop in/out as you scrub months; only the numbers change (updateTagCounts).
  const ever = {};
  for (const s of ALL) ever[s.tag] = (ever[s.tag] || 0) + 1;
  els.tagFilters.innerHTML = "";
  for (const [tag, label, color] of TAG_DEFS) {
    if (!ever[tag]) continue;                   // tradition with no shows at all → no pill
    const chip = document.createElement("button");
    chip.type = "button";
    chip.className = "tagchip";
    chip.style.setProperty("--tag-color", color);
    chip.dataset.tag = tag;
    const on = ACTIVE_TAGS.has(tag);
    chip.classList.toggle("on", on);
    chip.setAttribute("aria-pressed", on ? "true" : "false");
    chip.innerHTML = `<span class="tdot"></span>${esc(tagLabel(tag))}<span class="tcount">${ever[tag]}</span>`;
    chip.addEventListener("click", () => {
      if (ACTIVE_TAGS.has(tag)) ACTIVE_TAGS.delete(tag);
      else ACTIVE_TAGS.add(tag);
      chip.classList.toggle("on", ACTIVE_TAGS.has(tag));
      chip.setAttribute("aria-pressed", ACTIVE_TAGS.has(tag) ? "true" : "false");
      render();
    });
    tagCountSpans[tag] = chip.querySelector(".tcount");
    els.tagFilters.appendChild(chip);
  }
}

// Per-tradition count for the SELECTED month (and current search), ignoring the tag
// filter itself so each pill shows how many of its tradition are playing this month.
function updateTagCounts() {
  const q = fold(els.search.value.trim());
  const counts = {};
  for (const s of pool()) {
    if (!overlapsMonth(s)) continue;
    if (q && !matchesSearch(s, q)) continue;   // 與 visibleShows 同一組欄位(含 search),否則 pill 數字對不上清單(2026-07-10)
    counts[s.tag] = (counts[s.tag] || 0) + 1;
  }
  for (const tag in tagCountSpans) {
    const n = counts[tag] || 0;
    tagCountSpans[tag].textContent = n;
    tagCountSpans[tag].closest(".tagchip").classList.toggle("tag-zero", n === 0);
  }
}

// The timebar floats over the map; without this, dragging the slider also pans
// the Leaflet map underneath. Stop pointer/scroll events from reaching the map.
const timebarEl = document.getElementById("timebar");
if (timebarEl) {
  L.DomEvent.disableClickPropagation(timebarEl);  // mousedown/touchstart/dblclick/click
  L.DomEvent.disableScrollPropagation(timebarEl); // wheel-zoom over the bar
  ["pointerdown", "pointermove", "touchmove"].forEach((ev) =>
    L.DomEvent.on(timebarEl, ev, L.DomEvent.stopPropagation));
}

// ---------- Rendering helpers ----------
function posterStyle(show, w, h) {
  const t = thumb(show.image, w, h);
  return t ? `background-image:url('${cssUrl(t)}')` : "";
}
// 側欄縮圖延遲載入:原本 688 個劇目的 background-image 全部立即載(~100MB/首頁 load 21s)。
// 改成先寫 data-bg,IntersectionObserver 在捲進視野附近才套 background-image。
function posterLazyAttr(show, w, h) {
  const t = thumb(show.image, w, h);
  return t ? `data-bg="${cssUrl(t).replace(/"/g, "&quot;")}"` : "";
}
const bgIO = ("IntersectionObserver" in window)
  ? new IntersectionObserver((ents, ob) => {
      ents.forEach((e) => {
        if (!e.isIntersecting) return;
        const el = e.target, bg = el.getAttribute("data-bg");
        if (bg) { el.style.backgroundImage = `url('${bg}')`; el.removeAttribute("data-bg"); }
        ob.unobserve(el);
      });
    }, { rootMargin: "300px" })   // 提前 300px 開始載,捲到時已就緒
  : null;
function observeLazyThumbs(root) {
  (root || document).querySelectorAll("[data-bg]").forEach((el) => {
    if (bgIO) bgIO.observe(el);
    else { const bg = el.getAttribute("data-bg"); el.style.backgroundImage = `url('${bg}')`; el.removeAttribute("data-bg"); }
  });
}
function fallbackGlyph(show) {
  // shows with no poster (e.g. tour samples) get a music-note tile
  return show.image ? "" : `<span class="glyph">♪</span>`;
}

function posterMarkerIcon(show) {
  return L.divIcon({
    className: "mm-icon",
    html: `<div class="poster-pin ${show.image ? "" : "noimg"}" style="${posterStyle(show, 110, 150)}">${fallbackGlyph(show)}</div>`,
    iconSize: [52, 72],
    iconAnchor: [26, 72],
    popupAnchor: [0, -70],
  });
}

// Compact date: "7/31" within the current year, "2027/1/5" across years.
const _MON_EN = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
function fmtD(iso) {
  if (!iso) return "";
  const [y, m, d] = iso.split("-").map(Number);
  // en 一律月名(Jul 8):數字 7/8 對美式讀者可能被讀成 Aug 7(2026-07-09 使用者規格)
  if (document.documentElement.lang === "en") {
    return y === CUR_Y ? `${_MON_EN[m - 1]} ${d}` : `${_MON_EN[m - 1]} ${d}, ${y}`;
  }
  return y === CUR_Y ? `${m}/${d}` : `${y}/${m}/${d}`;
}
// ONE consistent date line, classified by what the viewer needs to know — NOT by
// which date fields happen to be present (the old logic had 8 phrasings):
//   • 長期上演   open-ended resident / rolling booking horizon (no real closing)
//   • 至 {end}   has a real last/closing date (tours, limited runs, on-sale-through)
//   • {start} 起 hasn't opened yet (future start, no end)
//   • (blank)    tour/limited missing dates = data gap, don't fake a status
function fmtDates(show) {
  const s = show.start_date, e = show.end_date;
  // Long-runner (open-ended) iff build_shows flagged it: end_rolling is set only for the
  // open-ended sit-down houses (Broadway / West End / Stage Entertainment), where the end
  // is a rolling booking horizon, not a closing. Everything else — tours, limited runs,
  // regional "resident"-mislabels (j25musical's 2.5D shows), and repertory titles with a
  // long but scattered date span — keeps its real "至 {end}".
  const longRun = show.end_rolling;
  if (longRun) return t("long_run");
  if (s && e && s === e) return fmtD(s);          // 單日場:顯示一個日期,不要「12/23 – 12/23」(2026-07-14,全庫 423 筆)
  if (s && e) return `${fmtD(s)} – ${fmtD(e)}`;   // 期間限定且起迄皆知 → 顯示完整範圍(2026-07-09 使用者規格)
  if (e) return t("date_until", { e: fmtD(e) });
  if (s && new Date(s) > TODAY0) return t("date_from", { s: fmtD(s) });
  // 起迄皆不明:來源只說「有在賣」,一個日期都沒給。以前回空字串 → 卡片日期欄整個空白,
  // 使用者看不出是「沒有這筆資料」還是「壞掉了」(2026-08-12 線上實測 4 筆全是空白)。
  if (!s && !e) return t("date_tbd");
  return "";
}

function tooltipHtml(show) {
  // hover card: bigger poster + key info
  const poster = thumb(show.image, 140, 196);
  const img = poster
    ? `<div class="tt-poster" style="background-image:url('${cssUrl(poster)}')"></div>`
    : `<div class="tt-poster noimg"><span class="glyph">♪</span></div>`;
  return `<div class="tt">${img}<div class="tt-meta">
      <div class="tt-title">${esc(canonTitle(show))}</div>
      ${show.venue ? `<div class="tt-sub">${esc(show.venue)}</div>` : ""}
      <div class="tt-sub">${esc(cityCountry(show))}</div>
      <div class="tt-date">${fmtDates(show)}</div>
    </div></div>`;
}

// Platform icon for a ticket host. Google's favicon service returns a generic globe
// for Chinese sites (damai/juooo…), so curated brand logos override it; everything
// else falls back to the live favicon (works for todaytix/ticketmaster/atg/…).
const LOGO_MAP = { "damai": "logos/damai.png", "juooo": "logos/juooo.png", "ticketmaster": "logos/ticketmaster.png", "opentix": "logos/opentix.png", "tixfun": "logos/tixfun.png", "mna.com": "logos/mna.png", "prazskemuzikaly": "logos/prazskemuzikaly.png", "broadway-show-tickets": "logos/headout.png", "toho.co": "logos/toho.png", "shcstheatre": "logos/shcstheatre.png", "theatre-orb": "logos/theatreorb.png", "teatrebarcelona": "logos/teatrebarcelona.png", "jegy.hu": "logos/jegyhu.png", "teatromadrid": "logos/teatromadrid.png", "platinumlist": "logos/platinumlist.png" };   // host-substring → rehosted logo (favicon too low-res / wrong for these)
function platformIcon(host) {
  // LOGO_MAP paths are repo-root-relative; prefix MM_BASE so they resolve from the
  // variant pages (/MusicalMap/zh-hant/…) instead of 404-ing. Favicon URLs are absolute.
  for (const k in LOGO_MAP) if (host.includes(k)) return (window.MM_BASE || "") + LOGO_MAP[k];
  return `https://www.google.com/s2/favicons?domain=${host}&sz=128`;
}
// host-substring → display name. Many scrapers omit a per-link label (e.g. opentix),
// which left tiles blank; this guarantees every ticket tile shows its platform name.
const PLATFORM_NAME = [
  ["damai", "大麥"], ["juooo", "聚橙"], ["maoyan", "貓眼"], ["opentix", "OPENTIX"],
  ["todaytix", "TodayTix"], ["ticketmaster", "Ticketmaster"], ["atgtickets", "ATG"],
  ["ticketworld", "TicketWorld"],
  ["londontheatre", "London Theatre"], ["kham", "寬宏"], ["udnfunlife", "udn 售票"],
  ["tixfun", "tixFun"], ["mna.com", "牛耳藝術"],
  ["interpark", "Interpark"], ["sistic", "SISTIC"], ["jegy", "jegy.hu"], ["polyt", "保利票務"],
  ["theatreinparis", "Theatre in Paris"], ["bol.pt", "BOL"], ["showtic", "Showtic"],
];
function platformName(host, fallback) {
  for (const [k, name] of PLATFORM_NAME) if (host.includes(k)) return name;
  // last resort: the bare domain (e.g. "example.com") rather than a blank label
  return fallback || (host.replace(/^www\./, "") || "");
}
// 資料層的 ticket link label 是寫死的中文(build_shows SOURCE_LABEL)——en 頁會冒出「Broadway票務」
// (2026-07-09 使用者抓到)。en 模式把已知中文 label 換英文;沒對到且含 CJK → 用網域名兜底。
const LABEL_EN = { "Broadway票務": "Broadway.com", "大麥": "Damai", "聚橙": "Juooo", "保利票務": "Poly Theatre",
  "票務": "Tickets", "官方售票": "Official tickets", "官方網站": "Official site", "售票連結": "Tickets",
  "四季官網": "Shiki Official", "宝塚官網": "Takarazuka Official", "Stage官網": "Stage Entertainment",
  "寬宏": "KHAM", "udn 售票": "udn tickets", "牛耳藝術": "MNA" };
function localizedLabel(raw, host, country) {
  if (document.documentElement.lang !== "en" || !raw) return raw;
  if (LABEL_EN[raw]) return LABEL_EN[raw];
  if (/[㐀-鿿぀-ヿ가-힯]/.test(raw)) {   // CJK 殘留 → 平台名/網域兜底
    const p = platformName(host || "", country);
    return /[㐀-鿿]/.test(p) ? (host || "").replace(/^www\./, "") : p;
  }
  return raw;
}

// 卡片「票務資訊 ⇄ 劇情」分頁切換。inline onclick 呼叫(popup 是動態字串,用全域函式最單純);
// 只在同一張卡(.pop-tabbed)內切換,不影響其他開著的卡。
window.mmTab = function (btn, which) {
  const box = btn.closest(".pop-tabbed");
  if (!box) return;
  box.querySelectorAll(".pop-tab").forEach((b) => b.setAttribute("aria-selected", String(b === btn)));
  box.querySelectorAll(".pop-pane").forEach((p) => { p.hidden = p.dataset.pane !== which; });
};

function popupHtml(show) {
  const poster = posterFull(show.image, 400);
  // 海報包一層 wrap:置中原比例完整海報+同圖模糊底(見 style.css .pop-poster-wrap 註解)
  const img = poster ? `<div class="pop-poster-wrap"><span class="pop-poster-bg" style="background-image:url('${esc(poster)}')"></span><img class="pop-poster" src="${esc(poster)}" alt=""></div>` : "";
  let links = Array.isArray(show.ticket_links) ? show.ticket_links.filter((l) => safeUrl(l.url)) : [];
  if (!links.length && safeUrl(show.ticket_url)) {
    links = [{ url: show.ticket_url, label: show.link_kind === "official" ? t("buy_official") : t("buy_tickets"), kind: show.link_kind }];
  }
  // Official site → hyperlink on the TITLE, NOT a ticket tile: the official site pays
  // no affiliate commission, so a prominent tile siphons clicks from the revenue-earning
  // ticketing platforms. Title-link keeps it one click away but secondary.
  const official = links.find((l) => l.kind === "official" && safeUrl(l.url));
  // square logo tiles — ticketing platforms only; tiles grow to fill the row (`n{count}`
  // lets CSS lay a lone source out wide instead of leaving the row blank).
  // Revenue-first: if a show has a commission-earning tile (a domain in AFFILIATE),
  // the non-earning tiles (teatromadrid/teatrebarcelona etc.) only dilute clicks away
  // from the monetised link. We RENDER them but HIDE them via CSS (.pop-tile-hidden)
  // rather than dropping them — so they can be switched back on any time by removing
  // that one CSS rule. Non-earning tiles stay visible when they're the SOLE way to buy
  // (an exclusive with no affiliate alternative). Official site stays on the title.
  const isRevenue = (u) => {
    try { const h = new URL(u).hostname;
      return AFF_TRACKING.test(h) || Object.keys(AFF).some((k) => h.includes(k)); }
    catch { return false; }
  };
  const ordered = links.filter((l) => l.kind !== "official");
  const hasRevenue = ordered.some((l) => isRevenue(l.url));
  const tilesHtml = ordered.map((l) => {
    const u = safeUrl(l.url); if (!u) return "";
    let host = ""; try { host = new URL(u).hostname; } catch { /* */ }
    const lab = esc(localizedLabel(l.label, host, l.country) || platformName(host, l.country));
    const ico = host ? platformIcon(host) : "";
    // Hover shows the CLEAN destination (href); the affiliate redirect is swapped in on
    // mousedown so the ugly viglink URL never appears in the status bar, yet click and
    // middle-click both still earn commission.
    const hidden = hasRevenue && !isRevenue(l.url) ? " pop-tile-hidden" : "";
    return `<a class="pop-tile${hidden}" href="${esc(u)}" data-aff="${esc(affiliateUrl(u))}" onmousedown="this.href=this.dataset.aff" target="_blank" rel="noopener" title="${lab}">
      <span class="pop-tile-ico">${ico ? `<img src="${esc(ico)}" alt="" loading="lazy" onerror="this.style.display='none'">` : ""}</span>
      <span class="pop-tile-label">${lab}</span>
      <span class="pop-tile-arr">→</span></a>`;
  }).join("");
  // 劇情簡介(依作品 group 查;只有繁中有 → 其他語系 SYN 空,退回原本純票務卡)。
  // 有簡介時:票務與劇情做「左右兩個分頁」,內容在同一塊區域切換;劇情用固定高度捲軸,
  // 卡片不因此變大(使用者規格:fit 原卡、劇情上下拖動、別大改字卡)。
  // 各語系有自己的 synopses 檔(en.json/zh-hant.json/zh-hans.json),記錄內只有一個語言鍵
  // ({zh:…}/{en:…}/{"zh-hans":…})。這裡語言無關地取出該筆簡介文字。
  const _synRec = show.group ? SYN[show.group] : null;
  const syn = _synRec ? (_synRec.zh || _synRec.en || _synRec["zh-hans"] || "") : "";
  let ticket = "";
  if (ordered.length && syn) {
    const story = syn.split(/\n{2,}/).map((p) => `<p>${esc(p)}</p>`).join("");
    ticket = `<div class="pop-tix pop-tabbed">
      <div class="pop-tabs" role="tablist">
        <button class="pop-tab" role="tab" aria-selected="true"  onclick="mmTab(this,'tix')">${esc(t("get_tickets"))}</button>
        <button class="pop-tab" role="tab" aria-selected="false" onclick="mmTab(this,'story')">${esc(t("story_tab"))}</button>
      </div>
      <div class="pop-pane" data-pane="tix"><div class="pop-tiles">${tilesHtml}</div></div>
      <div class="pop-pane" data-pane="story" hidden><div class="pop-story">${story}</div></div>
    </div>`;
  } else if (ordered.length) {
    ticket = `<div class="pop-tix"><div class="pop-tix-h">${esc(t("get_tickets"))}</div><div class="pop-tiles">${tilesHtml}</div></div>`;
  }
  // tour_name 通常是在地化/巡演製作名(「& Julia」「アラジン」「…North American Tour」),照用;
  // 但 TM 的 attraction 有時是「人名」(獨角戲演員,如 Harper Jones)——2~3 個首字大寫單字、
  // 無數字/標點、不含 musical/tour 等字眼 → 視為人名,回落正式劇名,別讓人名蓋掉劇名。
  const _tn = show.tour_name || "";
  const _looksPerson = /^[A-Z][a-zà-ÿ]+(?: [A-Z][a-zà-ÿ'’-]+){1,2}$/.test(_tn) && !/musical|tour|show|live|concert/i.test(_tn);
  const tname = (_tn && !_looksPerson) ? _tn.replace(show.title, canonTitle(show)) : "";
  const tourLine = "";  // production name (tour / localized version) now lives in the title itself
  const unverified = show.verified ? "" : `<div class="p-row warn">${esc(t("unverified_demo"))}</div>`;
  const titleTxt = esc(tname || canonTitle(show));  // the specific production's real name
  // Official site is reachable by clicking the title, but we DON'T advertise it (no arrow,
  // no hover styling): a visible link cue would funnel clicks to the non-paying official
  // site and away from the affiliate ticketing tiles. Looks like plain text; still a link.
  const title = official
    ? `<p class="p-title"><a class="p-title-link" href="${esc(official.url)}" data-aff="${esc(affiliateUrl(official.url))}" onmousedown="this.href=this.dataset.aff" target="_blank" rel="noopener">${titleTxt}</a></p>`
    : `<p class="p-title">${titleTxt}</p>`;
  // body width by tile count (DEFINITE px so Leaflet sizes the wrapper right — no overflow):
  // 3-tile row needs ~344px content; a lone source uses a narrower panel (less blank).
  const bodyW = ordered.length >= 3 ? 380 : 280;
  return `<div class="popup">${img}<div class="pop-body" style="width:${bodyW}px">
      ${title}
      ${tagBadge(show.tag)}
      ${tourLine}
      ${show.venue ? `<div class="p-row"><b>${esc(show.venue)}</b></div>` : ""}
      <div class="p-row">${esc(cityCountry(show))}</div>
      <div class="p-row">${fmtDates(show)}</div>
      ${ticket}${unverified}
    </div></div>`;
}

// ---------- Filtering ----------
// Which records back the current view: the live snapshot for THIS month onward,
// the immutable historical archive when the slider is dragged into the PAST. A run
// can start in year Y-1 and cross into Y, so a past view pools both year files.
function pool() {
  if (monthOffset >= 0) return ALL;
  const y = monthStart().getFullYear();
  return [...(ARCH[y] || []), ...(ARCH[y - 1] || [])];
}

// Lazy-load a past year's archive file once (no-op for years that don't exist or
// are already loaded). Returns a promise so the view can await it before render.
function loadArchiveYear(y) {
  if (ARCH[y]) return Promise.resolve();
  if (!ARCH_INDEX || !ARCH_INDEX.years || !(y in ARCH_INDEX.years)) { ARCH[y] = []; return Promise.resolve(); }
  if (archLoading[y]) return archLoading[y];
  archLoading[y] = fetch(`${window.MM_BASE || ""}data/archive/${y}.json`, { cache: "no-store" })
    .then((r) => r.json()).then((d) => { ARCH[y] = d.runs || []; })
    .catch(() => { ARCH[y] = []; });
  return archLoading[y];
}

function ensureArchiveForView() {
  if (monthOffset >= 0) return Promise.resolve();
  const y = monthStart().getFullYear();
  return Promise.all([loadArchiveYear(y), loadArchiveYear(y - 1)]);
}

// 搜尋命中判定(單一真相來源,pill 計數與清單/地圖共用,欄位一致含 search 大字串)
function matchesSearch(s, q) {
  return [s.title, s.city, s.venue, s.tour_name, s.alt, s.search].some((f) => fold(f).includes(q));
}
function visibleShows() {
  const q = fold(els.search.value.trim());
  return pool().filter((s) => {
    if (!overlapsMonth(s)) return false;
    if (ACTIVE_TAGS.size && !ACTIVE_TAGS.has(s.tag)) return false;
    if (!q) return true;
    return matchesSearch(s, q);
  });
}

// ---------- Render ----------
// 就地換既有 marker 的文字(語言切換用):不 clearLayers,故 marker 不會整批消失重建→不閃。
// 開著的 popup 用 setPopupContent 即時換內容,也不會關閉重開。
function relabelMarkers(shows) {
  const byId = {};
  shows.forEach((s) => { byId[s.id] = s; });
  for (const id in markerById) {
    const m = markerById[id], s = byId[id];
    if (!s) continue;
    m.setPopupContent(popupHtml(s));
    m.setTooltipContent(tooltipHtml(s));
    const ttl = [displayTitle([s]), s.city, s.country].filter(Boolean).join(" · ");
    m.options.title = m.options.alt = ttl;
    if (m._icon) { m._icon.title = ttl; m._icon.setAttribute("aria-label", ttl); }
  }
}
function render(inPlace) {
  inPlace = inPlace === true;   // 防呆:render 常被當 callback(search input/Promise.then)傳入 event/array;只有明確 true 才就地更新
  const shows = visibleShows();
  updateTagCounts();   // pill numbers reflect the selected month + search

  // markers
  const latlngs = [];
  if (inPlace) {
    relabelMarkers(shows);   // 顯示集合不變(通常是切語言)→ 就地換文字,避免整批 marker 閃爍
  } else {
  cluster.clearLayers();
  markerById = {};
  spreadSame(shows);   // fan same-venue shows into a tiny ring so they don't stack
  shows.forEach((s) => {
    if (typeof s.lat !== "number" || typeof s.lng !== "number") return;
    // a11y + hover title:海報 marker 是背景圖 div,螢幕閱讀器/滑鼠停留原本讀不到是哪一齣
    const mTitle = [displayTitle([s]), s.city, s.country].filter(Boolean).join(" · ");
    const m = L.marker([s.dlat, s.dlng], { icon: posterMarkerIcon(s), riseOnHover: true, title: mTitle, alt: mTitle, keyboard: true })
      .bindPopup(popupHtml(s), {
        maxWidth: Math.min(720, window.innerWidth - 40),  // never wider than the screen
        className: "mm-popup",
        closeOnClick: true,    // 點地圖空白處=關閉(真 click 才算;Leaflet 拖曳結束不觸發 click,drag 不會誤關)
        // autoPan 一律關(2026-07-14):桌面改由 map 級 popupopen「舒適區精準校正」接管
        // (量實際卡高、垂直置中於地圖頂~時間軸上緣;autoPan 只求「進視野」且在最小 zoom
        // 縱向無空間會卡死)。手機=底部 sheet 本就不需(2026-07-04 閃退案)。
        autoPan: false,
      })
      .bindTooltip(tooltipHtml(s), { direction: "top", offset: [0, -68], className: "mm-tip", opacity: 1 });
    // small card never coexists with the big card
    m.on("popupopen", () => { m.closeTooltip(); });
    m.on("tooltipopen", () => { if (m.isPopupOpen()) m.closeTooltip(); });
    // at low zoom: suppress the instantly-opened popup, fly in with ONE animation,
    // then show the card at a sensible scale. (zoomToShowLayer alone won't zoom
    // when the marker is already unclustered, so fly explicitly.)
    m.on("click", () => {
      if (map.getZoom() < 9) {
        map.closePopup();
        map.once("moveend", () => {
          if (m._icon) m.openPopup();
          else cluster.zoomToShowLayer(m, () => m.openPopup());  // got clustered at 12
        });
        map.flyTo(m.getLatLng(), 12, { animate: true, duration: 1.1 });
      }
    });
    cluster.addLayer(m);
    markerById[s.id] = m;
    latlngs.push([s.dlat, s.dlng]);
  });
  }

  // sidebar — one row per show; a show playing in multiple cities (e.g. Wicked
  // in London + New York) is a single entry you can expand to see each location.
  // Re-rendering (slider drag, search) must NOT collapse what the user expanded —
  // nor re-expand what the user collapsed (multi-city groups now default to open).
  const openKeys = new Set(
    [...els.list.querySelectorAll(".show-group.open")].map((el) => el.dataset.gkey));
  const closedKeys = new Set(
    [...els.list.querySelectorAll(".show-group.multi:not(.open)")].map((el) => el.dataset.gkey));
  els.list.innerHTML = "";
  if (NEARBY && USER_POS) {
    // 「附近」模式:平面清單,依距離由近到遠,最多 40 筆,每列加距離徽章。
    const near = shows
      .filter((s) => typeof s.lat === "number" && typeof s.lng === "number")
      .map((s) => ({ s, d: haversineKm(USER_POS, { lat: s.lat, lng: s.lng }) }))
      .sort((a, b) => a.d - b.d)
      .slice(0, 40);
    const hdr = document.createElement("li");
    hdr.className = "nearby-head";
    hdr.innerHTML = `<span>${esc(t("nearby_title"))}</span><button type="button" class="nearby-clear">${esc(t("nearby_clear"))}</button>`;
    hdr.querySelector(".nearby-clear").addEventListener("click", clearNearby);
    els.list.appendChild(hdr);
    if (!near.length) {
      const li = document.createElement("li"); li.className = "empty";
      li.textContent = t("locate_none"); els.list.appendChild(li);
    } else {
      let par = 0;
      near.forEach(({ s, d }) => {
        const li = showGroupItem([s], par++ % 2 ? "B" : "A");
        const loc = li.querySelector(".loc");
        const dist = d < 10 ? d.toFixed(1) : String(Math.round(d));
        if (loc) loc.insertAdjacentHTML("afterbegin", `<span class="dist">${dist} km</span>`);
        els.list.appendChild(li);
      });
      observeLazyThumbs(els.list);
    }
  } else if (!shows.length) {
    els.list.innerHTML = LOAD_FAILED
      ? `<li class="empty">${esc(t("load_error"))}<br><span>${esc(t("load_error_sub"))}</span></li>`
      : `<li class="empty">${esc(t("empty_title"))}<br><span>${esc(t("empty_sub"))}</span></li>`;
  } else {
    const byGroup = new Map();
    shows.forEach((s) => {
      const k = s.group || s.title;
      if (!byGroup.has(k)) byGroup.set(k, []);
      byGroup.get(k).push(s);
    });
    let parity = 0;
    // group the list by tradition (same category together), biggest category first,
    // then alphabetical within — no section headers, just a grouped order.
    const tagCount = {};
    shows.forEach((s) => { const tg = s.tag || "~"; tagCount[tg] = (tagCount[tg] || 0) + 1; });
    [...byGroup.entries()]
      .sort((a, b) => {
        const ta = a[1][0].tag || "~", tb = b[1][0].tag || "~";
        if (ta !== tb) return (tagCount[tb] - tagCount[ta]) || ta.localeCompare(tb);
        return displayTitle(a[1]).localeCompare(displayTitle(b[1]));
      })
      .forEach(([k, items]) => {
        // alternate each show's tint (teal / amber) so its extent reads at a glance
        const li = showGroupItem(items, parity++ % 2 ? "B" : "A");
        li.dataset.gkey = k;
        // 多城市一律預設展開(2026-07-03 指示:原本 >6 站的大巡演會折疊,現在通通展開);
        // 使用者手動收合的(closedKeys)重渲染時維持收合
        if (openKeys.has(k) || (items.length > 1 && !closedKeys.has(k))) li.classList.add("open");
        els.list.appendChild(li);
      });
    observeLazyThumbs(els.list);   // 縮圖延遲載入:只載捲進視野的
  }

  const groups = new Set(shows.map((s) => s.group || s.title)).size;
  const label = isThisMonth() ? t("playing_this_month") : t("playing_in", { ym: I18N.fmtYM(monthStart()) });
  els.count.textContent = LOAD_FAILED ? "" : t("count", { label, groups, n: shows.length });   // 載入失敗不顯示「0 部」假計數

  // fit to all markers once, on first load
  if (!inPlace && !didFitBounds && latlngs.length) {
    map.fitBounds(latlngs, { padding: [60, 60], maxZoom: 6 });
    didFitBounds = true;
  }
}

// Canonical display names for shows whose official title differs from sources.
// Keyed by the normalized `group` key (see build_shows.group_key).
const TITLE_OVERRIDES = {
  "phantom of the opera": "Phantom of the Opera", // official name dropped the "The"
};
function canonTitle(s) {
  return TITLE_OVERRIDES[s.group] || s.title;
}

// the cleanest title in a group (shortest) — "SIX" over "SIX: The Musical"
function displayTitle(items) {
  if (TITLE_OVERRIDES[items[0].group]) return TITLE_OVERRIDES[items[0].group];
  return items.map((s) => s.title).sort((a, b) => a.length - b.length)[0];
}

function fitShowBounds(items) {
  const pts = items.filter((s) => typeof s.lat === "number").map((s) => [s.lat, s.lng]);
  if (pts.length === 1) map.setView(pts[0], Math.max(map.getZoom(), 12), { animate: true });
  else if (pts.length > 1) map.fitBounds(pts, { padding: [70, 70], maxZoom: 6, animate: true });
}

// venue / city / date trio — the same little block for a single card and for each
// multi-city stop, so single and multi read as the same component. The status dot
// (with a gentle pulse) appears only on open-ended "long-running" runs.
// 城邦(新加坡/香港/澳門等)city===country 時只顯示一次,避免「新加坡, 新加坡」的重複
function cityCountry(s) {
  if (s.country && s.country !== s.city) return `${s.city}, ${s.country}`;
  return s.city || s.country || "";
}
function locTrio(s) {
  const dt = fmtDates(s);
  const ven = s.venue ? `<div class="ven">${esc(s.venue)}</div>` : "";
  const date = s.end_rolling
    ? `<div class="vdate now"><span class="vdot pulse"></span>${esc(dt)}</div>`
    : (dt ? `<div class="vdate">${esc(dt)}</div>` : "");
  const loc = cityCountry(s);
  return `${ven}<div class="city">${esc(loc)}</div>${date}`;
}

function showGroupItem(items, parity) {
  // 組內排序(2026-07-13 使用者規格):長期上演(end_rolling)拉到最前,
  // 順位=紐約 > 倫敦 > 其他長期上演 > 巡演/期間限定(後者維持原本的日期序;sort 穩定,同名次不動)。
  // 城市比對用資料層英文名(顯示層才翻中文),含 new york 涵蓋 "New York"/"New York, NY" 等變體。
  const _lrRank = (s) => {
    if (!s.end_rolling) return 3;
    const c = (s.city || "").toLowerCase();
    if (c.includes("new york")) return 0;
    if (c.includes("london")) return 1;
    return 2;
  };
  items = [...items].sort((a, b) => _lrRank(a) - _lrRank(b));
  const title = displayTitle(items);
  const li = document.createElement("li");
  const multi = items.length > 1;
  li.className = `show-group t${parity}${multi ? " multi" : ""}`;
  const first = items[0];
  const badge = first.verified ? "" : `<span class="badge-unverified">${esc(t("unverified"))}</span>`;
  // header poster = the canonical art: prefer a resident (Broadway/West End) production's
  // poster over tour/localized versions, so the big tile shows the classic key art.
  const imgShow = items.find((s) => s.end_rolling && s.image) || items.find((s) => s.image) || first;
  const thumb = `<div class="thumb ${imgShow.image ? "" : "noimg"}" ${posterLazyAttr(imgShow, 124, 186)}>${fallbackGlyph(imgShow)}</div>`;

  if (!multi) {
    li.innerHTML = `
      <div class="show-item single" data-id="${esc(first.id)}">
        ${thumb}
        <div class="info">
          <div class="title">${esc(title)}${badge}</div>
          <div class="loc">${locTrio(first)}</div>
        </div>
      </div>`;
    const head = li.querySelector(".show-item");
    head.addEventListener("click", () => focusShow(first));
    head.addEventListener("mouseenter", () => hoverShow(first, true));
    head.addEventListener("mouseleave", () => hoverShow(first, false));
    return li;
  }

  li.innerHTML = `
    <div class="show-item header has-children">
      ${thumb}
      <div class="info">
        <div class="title">${esc(title)}${badge}</div>
        <div class="city-count">${esc(t("city_count", { n: items.length }))}</div>
      </div>
      <span class="chev">▾</span>
    </div>
    <div class="stops"><div class="stops-inner">${items.map((s) =>
      `<div class="stop" data-id="${esc(s.id)}"><div class="stop-thumb ${s.image ? "" : "noimg"}" ${posterLazyAttr(s, 80, 120)}>${fallbackGlyph(s)}</div><div class="si">${locTrio(s)}</div><span class="chev-r">›</span></div>`).join("")}</div></div>`;

  li.querySelector(".show-item").addEventListener("click", () => {
    const opening = !li.classList.contains("open");
    li.classList.toggle("open", opening);
    if (opening) fitShowBounds(items);  // worldwide overview of this show
  });
  li.querySelectorAll(".stop").forEach((el) => {
    const s = items.find((x) => x.id === el.dataset.id);
    el.addEventListener("click", (e) => { e.stopPropagation(); focusShow(s); });
    el.addEventListener("mouseenter", () => hoverShow(s, true));
    el.addEventListener("mouseleave", () => hoverShow(s, false));
  });
  return li;
}

function setActive(id) {
  document.querySelectorAll("[data-id]").forEach((el) =>
    el.classList.toggle("active", el.dataset.id === id));
}

// two-way sync: hovering a list row previews its marker.
// Only when the marker is actually on screen as itself (m._icon exists) —
// clustered/hidden markers would show an orphan card over a cluster bubble.
function hoverShow(show, on) {
  const m = markerById[show.id];
  if (!m) return;
  if (on) { if (m._icon && !m.isPopupOpen()) m.openTooltip(); }
  else m.closeTooltip();
}

function focusShow(show) {
  const m = markerById[show.id];
  setActive(show.id);
  if (!m) return;
  // 與 marker 點擊同款「低倍先飛」:搜尋後 marker 少、最小 zoom 就已散開,zoomToShowLayer
  // 不會縮放而原地開卡——最小 zoom 世界圖上下貼邊,卡片超出地圖頂也無縱向空間可校正,
  // 卡死在畫面外(2026-07-14 使用者抓到:搜 mamma → 側欄點倫敦 Novello)。
  if (map.getZoom() < 9) {
    map.closePopup();
    map.once("moveend", () => {
      if (m._icon) m.openPopup();
      else cluster.zoomToShowLayer(m, () => m.openPopup());
    });
    map.flyTo(m.getLatLng(), 12, { animate: true, duration: 1.1 });
  } else {
    cluster.zoomToShowLayer(m, () => m.openPopup());
  }
}

// ---------- Boot ----------
// Variant pages (/en//zh-hans//zh-hant/) load their prebuilt, language-converted data file
// from an absolute base; legacy/dev context falls back to the canonical data/shows.json.
const MM_BASE = window.MM_BASE || "";
// ?v= 內容雜湊版號(每日 build 換)→ 可長快取+回訪走 304/快取,不必每次全下載 1.9MB。
// 與 <head> 的 preload 同 URL 才會被重用(2026-07-10 效能)。
const _dv = window.MM_DATA_VER ? `?v=${window.MM_DATA_VER}` : "";
function showsUrl(v) {
  return v ? `${MM_BASE}data/variants/shows.${v}.json${_dv}` : "data/shows.json";
}
function synUrl(v) { return `${MM_BASE}data/synopses/${v || "zh-hant"}.json${_dv}`; }
const SHOWS_URL = showsUrl(window.MM_VARIANT);
// 語言資料快取:切語言/preload 用,同語言不重抓。{shows, generated, syn}
const LANG_CACHE = {};
async function loadLangData(v) {
  if (LANG_CACHE[v]) return LANG_CACHE[v];
  const [sd, syd] = await Promise.all([
    fetch(showsUrl(v)).then((r) => r.json()).catch(() => ({ shows: [] })),
    fetch(synUrl(v)).then((r) => (r.ok ? r.json() : { syn: {} })).catch(() => ({ syn: {} })),
  ]);
  LANG_CACHE[v] = { shows: sd.shows || [], generated: (sd.meta && sd.meta.generated_at) || "", syn: syd.syn || {} };
  return LANG_CACHE[v];
}
async function boot() {
  try {
    const data = await loadLangData(window.MM_VARIANT || "zh-hant");
    ALL = data.shows;
    DATA_UPDATED = data.generated;
    renderDataNote();
    // 劇情簡介:各語系自己的檔(en/zh-hant/zh-hans);無檔則 SYN 空、卡片只有票務分頁
    for (const k in SYN) delete SYN[k];
    Object.assign(SYN, data.syn);
  } catch (e) {
    // 舊實作把錯誤寫進已不存在的 #data-note(黑洞),然後照常渲染出「0 部音樂劇/試試清除搜尋」
    // 的誤導空狀態 — 改設旗標,render 的空狀態分支顯示真正的錯誤訊息
    LOAD_FAILED = true;
    console.error("shows data load failed (local dev: serve over http, see README)", e);
  }
  // historical archive index (enables dragging the timeline into the past)
  if (SHOW_HISTORY) {
    try {
      ARCH_INDEX = await (await fetch(`${MM_BASE}data/archive/index.json`, { cache: "no-store" })).json();
    } catch (e) { ARCH_INDEX = null; }   // archive optional — map still works without it
  }
  buildTagFilters();
  recomputeRange();
  render();
  // Reveal the interactive UI now that the real sidebar/map are rendered, so the
  // crawler-only prerendered list never flashes during load / language switch.
  document.body.classList.add("ready");
  // 背景 preload 另外兩種語言的資料 → 之後切語言瞬間完成(使用者需求:立馬切、畫面不動)
  const _idle = window.requestIdleCallback || function (f) { return setTimeout(f, 1500); };
  _idle(function () {
    ["en", "zh-hant", "zh-hans"].forEach(function (v) {
      if (v !== (window.MM_VARIANT || "zh-hant")) loadLangData(v).catch(function () {});
    });
  });
}


// 就地切換語言(i18n.switchTo 觸發):換該語言的資料+簡介、重繪,並保留畫面狀態——
// 搜尋字(input 值不動)、地圖中心/縮放(map 物件不動)、月份(monthOffset 不動)、開著的劇卡(用 id 重開)。
window.addEventListener("mm-langchange", async function () {
  // 捕捉「當前開著的卡 + 它開在哪個 tab」必須在任何 render/clearLayers 之前(否則卡已被關掉,撈不到)。
  let keepOpen = null, keepTab = "tix";
  for (const id in markerById) {
    const mm = markerById[id];
    if (mm && mm.isPopupOpen && mm.isPopupOpen()) {
      keepOpen = id;
      const el = mm.getPopup && mm.getPopup() && mm.getPopup().getElement();
      const story = el && el.querySelector('.pop-tab[onclick*="story"]');
      if (story && story.getAttribute("aria-selected") === "true") keepTab = "story";
      break;
    }
  }
  const v = (window.MM_VARIANT) || (window.I18N && window.I18N.variant);
  // 變體頁(地圖 app)→ 就地換該語言的資料+簡介;非變體/無 loadLangData → 只重繪(沿用舊行為)。
  if (v && typeof loadLangData === "function") {
    let data;
    try { data = await loadLangData(v); } catch (e) { data = null; }
    if (data && data.shows.length) {
      ALL = data.shows;
      DATA_UPDATED = data.generated;
      for (const k in SYN) delete SYN[k];
      Object.assign(SYN, data.syn);
    }
  }
  buildTagFilters();   // 重貼傳統別 pill 文字(ACTIVE_TAGS 篩選狀態保留)
  renderDataNote();

  const restoreTab = function (m) {   // 還原切換前開著的 tab(劇情),否則卡會落回票務
    if (keepTab !== "story" || !m || !m.getPopup || !m.getPopup()) return;
    const el = m.getPopup().getElement();
    const story = el && el.querySelector('.pop-tab[onclick*="story"]');
    if (story) window.mmTab(story, "story");
  };

  // 顯示集合是否不變?(搜尋/月份/篩選沿用,通常只是換語言→集合一樣)。一樣就「就地換文字」不閃;
  // 少數情況(如用某語言才有的字搜尋)集合會變→走完整 render() 重建。
  const nextIds = visibleShows().map((s) => s.id);
  const sameSet = nextIds.length === Object.keys(markerById).length && nextIds.every((id) => markerById[id]);

  if (sameSet) {
    render(true);                 // 就地:marker 不消失、開著的卡用 setPopupContent 即時換內容不關閉
    if (keepOpen && markerById[keepOpen]) restoreTab(markerById[keepOpen]);
  } else {
    render(false);                // 集合變了→完整重建,再把原本開著的卡在新語言重開
    if (keepOpen && markerById[keepOpen]) {
      const m = markerById[keepOpen];
      const doOpen = function () { m.openPopup(); restoreTab(m); };
      if (m._icon) doOpen();
      else if (cluster.zoomToShowLayer) cluster.zoomToShowLayer(m, doOpen);
      else doOpen();
    }
  }
});

// Trim the slider to where the data actually goes — the latest show start month
// (+1 month buffer). No point dragging to 2029 when nothing plays past 2028.
function recomputeRange() {
  let maxOff = 1;
  for (const s of ALL) {
    if (!s.start_date) continue;
    const d = localDate(s.start_date);   // 本地解析(同 overlapsMonth,避免 UTC 邊界差月)
    if (!d) continue;
    const off = (d.getFullYear() - CUR_Y) * 12 + (d.getMonth() - CUR_M);
    if (off > maxOff) maxOff = off;
  }
  // Slider reaches exactly 1 year ahead, always — auto-rolling because CUR_Y/CUR_M are
  // taken from today at load (2026-06 → 2027-06; on 2026-07-01 → 2027-07). We keep the
  // full year reachable even if the data doesn't extend that far (maxOff unused for the
  // cap), matching the open-run display horizon (OPEN_RUN_HORIZON).
  void maxOff;
  MAX_MONTHS = 12;
  els.tRange.max = MAX_MONTHS;
  const d = new Date(CUR_Y, CUR_M + MAX_MONTHS, 1);
  els.tMonth.max = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`;

  // Extend into the PAST as far as the archive goes (Jan of its earliest year)。
  // 滑桿只開最近 18 個月:earliest 直接當滑桿 min 會被深歷史撐爆(archive 含 Phantom
  // 1988 起的長跑劇,曾連 1229 髒年都進來→滑桿近萬格,一格=0.01% 拖不動;2026-07-14
  // 深稽核)。更早的月份用月曆 picker 鍵入(tMonth.min 仍=earliest,深歷史入口不關)。
  if (ARCH_INDEX && ARCH_INDEX.years && Object.keys(ARCH_INDEX.years).length) {
    const earliest = Math.min(...Object.keys(ARCH_INDEX.years).map(Number));
    MIN_MONTHS = (earliest - CUR_Y) * 12 - CUR_M;   // offset to that year's January
    els.tRange.min = Math.max(MIN_MONTHS, -18);
    els.tMonth.min = `${earliest}-01`;
  }
}

els.search.addEventListener("input", () => render());
els.search.addEventListener("keydown", (e) => { if (e.key === "Escape") { els.search.value = ""; render(); } });
// ?q= 深連結搜尋:讓 WebSite SearchAction(sitelinks searchbox)真的能用,並支援分享搜尋結果連結。
// 例 /en/?q=wicked → 開頁即以 wicked 篩選(2026-07-10)。
try { const _q = new URLSearchParams(location.search).get("q"); if (_q) { els.search.value = _q; } } catch (e) {}

// ---------- Time bar (month slider + month picker, kept in sync) ----------
// Granularity is one MONTH: dragging selects a month, and any show whose run
// crosses that month appears (see overlapsMonth). No day-level precision.
function setMonth(offset, { fromSlider = false, fromPicker = false } = {}) {
  monthOffset = Math.min(Math.max(offset, MIN_MONTHS), MAX_MONTHS);  // clamp [earliest archive, +MAX_MONTHS]
  if (!fromSlider) els.tRange.value = monthOffset;
  if (!fromPicker) els.tMonth.value = selYM();
  // 顯示層 label 一律用「頁面語言」格式化(原生 input 只當透明點擊層,它的字樣跟瀏覽器語言走)
  { const ym = I18N.fmtYM(monthStart());
    const lbl = document.getElementById("time-month-label"); if (lbl) lbl.textContent = ym;
    els.tRange.setAttribute("aria-valuetext", ym); }   // 螢幕閱讀器念出「幾月」而非 0-36 數字
  els.tToday.style.visibility = monthOffset === 0 ? "hidden" : "visible";
  // past months read the archive (lazy-loaded) — wait for it, then render
  ensureArchiveForView().then(() => render());
}

els.tRange.max = MAX_MONTHS;
els.tMonth.min = selYM();                                    // this month
els.tMonth.max = `${new Date(CUR_Y, CUR_M + MAX_MONTHS, 1).getFullYear()}-${String(new Date(CUR_Y, CUR_M + MAX_MONTHS, 1).getMonth() + 1).padStart(2, "0")}`;
// rAF-throttled: dragging fires dozens of input events; rebuild at most once a frame
let sliderRaf = null;
els.tRange.addEventListener("input", () => {
  if (sliderRaf) return;
  sliderRaf = requestAnimationFrame(() => {
    sliderRaf = null;
    setMonth(Number(els.tRange.value), { fromSlider: true });
  });
});
els.tMonth.addEventListener("change", () => {
  const [y, m] = els.tMonth.value.split("-").map(Number);
  if (y && m) setMonth((y - CUR_Y) * 12 + (m - 1 - CUR_M), { fromPicker: true });
});
els.tToday.addEventListener("click", () => { stopPlay(); setMonth(0); });

// play: step one month per tick to watch tours travel across the calendar
let playTimer = null;
function stopPlay() {
  if (playTimer) { clearInterval(playTimer); playTimer = null; els.tPlay.textContent = "▶"; els.tPlay.classList.remove("playing"); }
}
els.tPlay.addEventListener("click", () => {
  if (playTimer) { stopPlay(); return; }
  els.tPlay.textContent = "⏸"; els.tPlay.classList.add("playing");
  playTimer = setInterval(() => {
    if (monthOffset >= MAX_MONTHS) { stopPlay(); return; }
    setMonth(monthOffset + 1);
  }, 900);
});

setMonth(0);
boot();
