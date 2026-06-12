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

const map = L.map("map", { zoomControl: true, worldCopyJump: true }).setView([30, 10], 2);
const streets = L.tileLayer("https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png", {
  attribution: "&copy; OpenStreetMap &copy; CARTO", subdomains: "abcd", maxZoom: 19,
}).addTo(map);
const satellite = L.tileLayer(
  "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}", {
    attribution: "Tiles &copy; Esri, Maxar, Earthstar Geographics", maxZoom: 19,
  });
L.control.layers({ "地圖": streets, "衛星": satellite }, null, { position: "topright" }).addTo(map);

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
const els = { search: document.getElementById("vsearch"), count: document.getElementById("vcount") };

function render() {
  const q = norm(els.search.value);
  const shown = q ? ALL.filter((v) => norm(v.search || v.name).includes(q)) : ALL;
  cluster.clearLayers();
  const markers = shown.map((v) =>
    L.marker([v.lat, v.lng], { icon: dot, riseOnHover: true })
      .bindPopup(`<b>${esc(v.name)}</b><br><span style="color:#64748b">${esc(v.city || "")}${v.country ? ", " + esc(v.country) : ""}</span>`, { maxWidth: 280 }));
  cluster.addLayers(markers);
  els.count.textContent = `${shown.length.toLocaleString()} 個劇院` + (q ? `（共 ${ALL.length.toLocaleString()}）` : "");
}

const dot = L.divIcon({ className: "venue-dot-wrap", html: '<div class="venue-dot"></div>', iconSize: [12, 12] });

async function boot() {
  try {
    const data = await fetch("data/venues_catalog.json", { cache: "no-store" }).then((r) => r.json());
    ALL = (data.venues || []).filter((v) => typeof v.lat === "number" && typeof v.lng === "number");
  } catch (e) {
    els.count.textContent = "⚠ 無法載入場館資料（需用本機 server 開啟）";
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

boot();
