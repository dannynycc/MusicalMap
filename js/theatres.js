/* All-theatres map — every venue in data/venues_catalog.json shown with the same
 * green cluster circles as the main map. Multilingual search (matches the catalog
 * `search` blob: EN + native + simplified/traditional + diacritic-folded). */

const esc = (v) => String(v ?? "").replace(/[&<>"']/g, (c) =>
  ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

// must mirror gen_catalog.py _clean(): lowercase, 臺→台, fold Latin diacritics
// (not CJK/Cyrillic), strip every bracket/quote/separator.
const PUNCT = /[()\[\]{}（）［］｛｝「」『』【】〔〕《》〈〉<>＜＞"'`＂＇“”‘’｀、・·,，:：/／|｜~～\-－—–]+/g;
const FOLD = { "ł": "l", "ø": "o", "ß": "ss", "đ": "d", "æ": "ae", "œ": "oe", "ı": "i", "ð": "d", "þ": "th" };
function foldLatin(s) {
  let o = "";
  for (const ch of s) {
    if (FOLD[ch]) { o += FOLD[ch]; continue; }
    const d = ch.normalize("NFKD");
    o += (d.charCodeAt(0) < 128 && /[a-z]/.test(d[0])) ? d.replace(/[̀-ͯ]/g, "") : ch;
  }
  return o;
}
const norm = (s) => foldLatin((s || "").toLowerCase().replace(/臺/g, "台")).replace(PUNCT, " ").replace(/\s+/g, " ").trim();

// i18n:走 mm-strings 的 MM_T(2026-07-09 修復:原呼叫 i18n.js 的 t(),但本頁已改載 mm-strings、
// i18n.js 未載入 → 頂層 ReferenceError 整頁 JS 死亡,地圖/搜尋/計數全滅)。MM_T 不做插值,這裡補。
const t = (k, vars) => {
  let s = (window.MM_T ? window.MM_T(k) : k);
  for (const n in (vars || {})) s = s.replace("{" + n + "}", vars[n]);
  return s;
};

const map = L.map("map", { zoomControl: true, worldCopyJump: true }).setView([30, 10], 2);
const streets = L.tileLayer("https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png", {
  attribution: "&copy; OpenStreetMap &copy; CARTO", subdomains: "abcd", maxZoom: 19,
}).addTo(map);
const satellite = L.tileLayer(
  "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}", {
    attribution: "Tiles &copy; Esri, Maxar, Earthstar Geographics", maxZoom: 19,
  });
L.control.layers({ [t("map")]: streets, [t("satellite")]: satellite }, null, { position: "topright" }).addTo(map);

const cluster = L.markerClusterGroup({
  maxClusterRadius: 50, showCoverageOnHover: false, chunkedLoading: true,
  iconCreateFunction: (c) => {                       // same √n sizing as the main map
    const n = c.getChildCount();
    const size = Math.round(Math.max(30, Math.min(118, 20 + Math.sqrt(n) * 7.5)));
    const fs = Math.round(Math.max(11, size * 0.34));
    return L.divIcon({
      html: `<div class="mm-cluster" style="width:${size}px;height:${size}px;font-size:${fs}px"><span>${n}</span></div>`,
      className: "mm-cluster-wrap", iconSize: [size, size],
    });
  },
});
map.addLayer(cluster);

let ALL = [];
const els = {
  search: document.getElementById("vsearch"),
  count: document.getElementById("vcount"),
  results: document.getElementById("vresults"),
};

const popupHtml = (v) =>
  `<b>${esc(v.name)}</b><br><span style="color:#64748b">${esc(v.city || "")}${v.country ? ", " + esc(v.country) : ""}</span>`;

function render() {
  const q = norm(els.search.value);
  const shown = q ? ALL.filter((v) => norm(v.search || v.name).includes(q)) : ALL;
  cluster.clearLayers();
  const markers = shown.map((v) =>
    L.marker([v.lat, v.lng], { icon: dot, riseOnHover: true }).bindPopup(popupHtml(v), { maxWidth: 280 }));
  cluster.addLayers(markers);
  els.count.textContent = q
    ? t("v_count_filtered", { n: shown.length.toLocaleString(), total: ALL.length.toLocaleString() })
    : t("v_count", { n: shown.length.toLocaleString() });
  renderResults(q, shown);
}

// Clickable result list: searching shows the matches so you can pick one and fly to
// it (the markers are clustered, so a count alone gives you nothing to click). Built
// with DOM nodes + textContent — no innerHTML — so scraped names can't inject markup.
const RESULT_CAP = 60;
function renderResults(q, shown) {
  const ul = els.results;
  ul.textContent = "";
  if (!q) { ul.hidden = true; ul._items = []; return; }
  const top = shown.slice(0, RESULT_CAP);
  ul._items = top;
  top.forEach((v, i) => {
    const li = document.createElement("li");
    li.dataset.i = i;
    const nm = document.createElement("span"); nm.className = "vn"; nm.textContent = v.name || "";
    const loc = document.createElement("span"); loc.className = "vc";
    loc.textContent = (v.city || "") + (v.country ? ", " + v.country : "");
    li.append(nm, document.createElement("br"), loc);
    ul.appendChild(li);
  });
  if (shown.length > RESULT_CAP) {
    const more = document.createElement("li");
    more.className = "more";
    more.textContent = t("v_more", { n: shown.length - RESULT_CAP });
    ul.appendChild(more);
  }
  ul.hidden = false;
}

function flyToVenue(v) {
  const pop = L.popup({ maxWidth: 280 }).setLatLng([v.lat, v.lng]).setContent(popupHtml(v));
  map.flyTo([v.lat, v.lng], 16, { duration: 0.8 });
  map.once("moveend", () => pop.openOn(map));   // open after the flight settles
}

const dot = L.divIcon({ className: "venue-dot-wrap", html: '<div class="venue-dot"></div>', iconSize: [12, 12] });

async function boot() {
  try {
    const data = await fetch("data/venues_catalog.json", { cache: "no-store" }).then((r) => r.json());
    ALL = (data.venues || []).filter((v) => typeof v.lat === "number" && typeof v.lng === "number");
  } catch (e) {
    els.count.textContent = t("load_error_venues");
    console.error(e); return;
  }
  render();
}

let raf = null;
els.search.addEventListener("input", () => {
  if (raf) cancelAnimationFrame(raf);
  raf = requestAnimationFrame(render);
});
els.search.addEventListener("keydown", (e) => { if (e.key === "Escape") { els.search.value = ""; render(); } });

// click a result → fly to that venue and open its popup
els.results.addEventListener("click", (e) => {
  const li = e.target.closest("li[data-i]");
  if (!li) return;
  const v = els.results._items[+li.dataset.i];
  if (v) flyToVenue(v);
});

window.addEventListener("mm-langchange", render);   // re-render count/results in the new language

boot();
