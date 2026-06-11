/* MusicalMap — frontend
 * Reads data/shows.json and renders an interactive map + synced sidebar.
 * Data layer (scrapers) and presentation layer (this file) are decoupled.
 *
 * Security: show data is UNTRUSTED (comes from scrapers). All text is escaped
 * via esc(); ticket + image URLs are protocol-whitelisted.
 */

const TODAY = new Date();

// ---------- safety helpers (untrusted scraped data) ----------
function esc(v) {
  return String(v ?? "")
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;").replace(/'/g, "&#39;");
}
function safeUrl(u) {
  if (!u) return null;
  try {
    const p = new URL(u, location.href);
    return ["http:", "https:"].includes(p.protocol) ? p.href : null;
  } catch { return null; }
}

// CDN-side thumbnailing: request a small CROPPED square-ish poster for markers
// and list thumbnails. Contentful / imgix / craft.cloud take different params.
function thumb(url, w, h) {
  const u = safeUrl(url);
  if (!u) return null;
  if (u.includes("ctfassets.net")) return `${u}?w=${w}&h=${h}&fit=fill&fm=webp&q=70`;
  if (u.includes("imgix") || u.includes("headout")) return `${u}?w=${w}&h=${h}&fit=crop&auto=format&q=70`;
  if (u.includes("craft.cloud")) return `${u}?width=${w}&height=${h}&fit=crop`;
  return u;
}

// Full uncropped poster (preserve aspect ratio) for the popup showcase.
function posterFull(url, w) {
  const u = safeUrl(url);
  if (!u) return null;
  if (u.includes("ctfassets.net")) return `${u}?w=${w}&fm=webp&q=80`;
  if (u.includes("imgix") || u.includes("headout")) return `${u}?w=${w}&auto=format&q=80`;
  if (u.includes("craft.cloud")) return `${u}?width=${w}`;
  return u;
}

// ---------- "is this show playing right now?" ----------
function isPlayingNow(show, today = TODAY) {
  const start = show.start_date ? new Date(show.start_date) : null;
  const end = show.end_date ? new Date(show.end_date) : null;
  if (start && today < start) return false;
  if (end && today > end) return false;
  return true;
}

// ---------- Map ----------
const map = L.map("map", { zoomControl: true, worldCopyJump: true }).setView([42, -40], 3);
// Light, clean basemap (CARTO Voyager) — readable in dark mode, soft roads/water.
L.tileLayer("https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png", {
  attribution: "&copy; OpenStreetMap &copy; CARTO",
  subdomains: "abcd", maxZoom: 19,
}).addTo(map);
const cluster = L.markerClusterGroup({
  maxClusterRadius: 45,
  spiderfyOnMaxZoom: true,
  showCoverageOnHover: false,
  // size the bubble by how many shows it holds (bigger count → bigger circle)
  iconCreateFunction: (c) => {
    const n = c.getChildCount();
    // linear scaling for an obvious size difference (small 30px → large 88px)
    const size = Math.round(Math.max(30, Math.min(88, 22 + n * 2)));
    const fs = Math.round(Math.max(12, size * 0.34));
    return L.divIcon({
      html: `<div class="mm-cluster" style="width:${size}px;height:${size}px;font-size:${fs}px"><span>${n}</span></div>`,
      className: "mm-cluster-wrap",
      iconSize: [size, size],
    });
  },
});
map.addLayer(cluster);

// ---------- State ----------
let ALL = [];
let markerById = {};
let didFitBounds = false;

const els = {
  list: document.getElementById("show-list"),
  count: document.getElementById("count"),
  search: document.getElementById("search"),
  filters: document.querySelectorAll('#filters input[type="checkbox"]'),
  note: document.getElementById("data-note"),
};

// ---------- Rendering helpers ----------
function posterStyle(show, w, h) {
  const t = thumb(show.image, w, h);
  return t ? `background-image:url('${esc(t)}')` : "";
}
function fallbackGlyph(show) {
  // shows with no poster (e.g. tour samples) get a music-note tile
  return show.image ? "" : `<span class="glyph">♪</span>`;
}

function posterMarkerIcon(show) {
  return L.divIcon({
    className: "mm-icon",
    html: `<div class="poster-pin ${esc(show.type)} ${show.image ? "" : "noimg"}" style="${posterStyle(show, 110, 150)}">${fallbackGlyph(show)}</div>`,
    iconSize: [52, 72],
    iconAnchor: [26, 72],
    popupAnchor: [0, -70],
  });
}

function fmtDates(show) {
  if (show.type === "resident") return show.end_date ? `售票至 ${esc(show.end_date)}` : "常駐演出中";
  return `${esc(show.start_date || "?")} – ${esc(show.end_date || "?")}`;
}

function tooltipHtml(show) {
  // hover card: bigger poster + key info
  const poster = thumb(show.image, 140, 196);
  const img = poster
    ? `<div class="tt-poster" style="background-image:url('${esc(poster)}')"></div>`
    : `<div class="tt-poster noimg"><span class="glyph">♪</span></div>`;
  return `<div class="tt">${img}<div class="tt-meta">
      <div class="tt-title">${esc(canonTitle(show))}</div>
      <div class="tt-sub">${esc(show.venue)}</div>
      <div class="tt-sub">${esc(show.city)}, ${esc(show.country)}</div>
      <div class="tt-date">${fmtDates(show)}</div>
    </div></div>`;
}

function popupHtml(show) {
  const tag = show.type === "tour" ? "巡演" : "常駐";
  const poster = posterFull(show.image, 400);
  const img = poster ? `<img class="pop-poster" src="${esc(poster)}" alt="">` : "";
  const url = safeUrl(show.ticket_url);
  const ticket = url ? `<a class="pop-cta" href="${esc(url)}" target="_blank" rel="noopener">前往官方售票頁 →</a>` : "";
  const tname = show.tour_name ? show.tour_name.replace(show.title, canonTitle(show)) : "";
  const tourLine = show.type === "tour" && tname ? `<div class="p-row"><b>${esc(tname)}</b></div>` : "";
  const unverified = show.verified ? "" : `<div class="p-row warn">⚠ 未驗證（示範資料）</div>`;
  return `<div class="popup">${img}<div class="pop-body">
      <span class="p-tag ${esc(show.type)}">${tag}</span>
      <p class="p-title">${esc(canonTitle(show))}</p>
      ${tourLine}
      <div class="p-row"><b>${esc(show.venue)}</b></div>
      <div class="p-row">${esc(show.city)}, ${esc(show.country)}</div>
      <div class="p-row">${fmtDates(show)}</div>
      ${ticket}${unverified}
    </div></div>`;
}

// ---------- Filtering ----------
function activeTypes() {
  const on = new Set();
  els.filters.forEach((cb) => { if (cb.checked) on.add(cb.dataset.filter); });
  return on;
}
function visibleShows() {
  const q = els.search.value.trim().toLowerCase();
  const types = activeTypes();
  return ALL.filter((s) => {
    if (!types.has(s.type)) return false;
    if (!isPlayingNow(s)) return false;
    if (!q) return true;
    return [s.title, s.city, s.venue, s.tour_name].some((f) => (f || "").toLowerCase().includes(q));
  });
}

// ---------- Render ----------
function render() {
  const shows = visibleShows();

  // markers
  cluster.clearLayers();
  markerById = {};
  const latlngs = [];
  shows.forEach((s) => {
    if (typeof s.lat !== "number" || typeof s.lng !== "number") return;
    const m = L.marker([s.lat, s.lng], { icon: posterMarkerIcon(s), riseOnHover: true })
      .bindPopup(popupHtml(s), { maxWidth: 620, className: "mm-popup" })
      .bindTooltip(tooltipHtml(s), { direction: "top", offset: [0, -68], className: "mm-tip", opacity: 1 });
    // at low zoom, clicking flies in first so the card shows at a sensible scale
    m.on("click", () => { if (map.getZoom() < 9) map.flyTo(m.getLatLng(), 12, { animate: true }); });
    cluster.addLayer(m);
    markerById[s.id] = m;
    latlngs.push([s.lat, s.lng]);
  });

  // sidebar — one row per show; a show playing in multiple cities (e.g. Wicked
  // in London + New York) is a single entry you can expand to see each location.
  els.list.innerHTML = "";
  if (!shows.length) {
    els.list.innerHTML = `<li class="empty">沒有符合的音樂劇<br><span>試試清除搜尋或開啟其他篩選</span></li>`;
  } else {
    const byGroup = new Map();
    shows.forEach((s) => {
      const k = s.group || s.title;
      if (!byGroup.has(k)) byGroup.set(k, []);
      byGroup.get(k).push(s);
    });
    [...byGroup.values()]
      .sort((a, b) => displayTitle(a).localeCompare(displayTitle(b)))
      .forEach((items) => els.list.appendChild(showGroupItem(items)));
  }

  els.count.textContent = `目前上演中：${shows.length} 部`;

  // fit to all markers once, on first load
  if (!didFitBounds && latlngs.length) {
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

function showGroupItem(items) {
  const title = displayTitle(items);
  const li = document.createElement("li");
  li.className = "show-group";
  const first = items[0];
  const multi = items.length > 1;
  const badge = first.verified ? "" : `<span class="badge-unverified">未驗證</span>`;
  const cities = [...new Set(items.map((s) => s.city))];
  const sub = multi
    ? `${cities.map(esc).join("、")}　·　${items.length} 個地點`
    : first.type === "tour" ? `${esc(first.city)} · ${fmtDates(first)}` : esc(first.venue);
  const imgShow = items.find((s) => s.image) || first;

  li.innerHTML = `
    <div class="show-item${multi ? " has-children" : ""}"${multi ? "" : ` data-id="${esc(first.id)}"`}>
      <div class="thumb ${imgShow.image ? "" : "noimg"}" style="${posterStyle(imgShow, 60, 84)}">${fallbackGlyph(imgShow)}</div>
      <div class="info">
        <div class="title"><span class="type-dot ${esc(first.type)}"></span>${esc(title)}${badge}${multi ? `<span class="loc-count">${items.length} 地</span>` : ""}</div>
        <div class="meta">${sub}</div>
      </div>
      ${multi ? `<span class="chev">▾</span>` : ""}
    </div>
    ${multi ? `<ul class="sublist">${items.map((s) => `
      <li class="sub-item" data-id="${esc(s.id)}">
        <span class="type-dot ${esc(s.type)}"></span>
        <span class="sub-venue">${esc(s.venue)}</span>
        <span class="sub-city">${esc(s.city)}</span>
      </li>`).join("")}</ul>` : ""}`;

  const head = li.querySelector(".show-item");
  if (multi) {
    head.addEventListener("click", () => {
      const opening = !li.classList.contains("open");
      document.querySelectorAll(".show-group.open").forEach((el) => el !== li && el.classList.remove("open"));
      li.classList.toggle("open", opening);
      if (opening) fitShowBounds(items);  // worldwide overview of this show
    });
    li.querySelectorAll(".sub-item").forEach((el) => {
      const s = items.find((x) => x.id === el.dataset.id);
      el.addEventListener("click", (e) => { e.stopPropagation(); focusShow(s); });
      el.addEventListener("mouseenter", () => hoverShow(s, true));
      el.addEventListener("mouseleave", () => hoverShow(s, false));
    });
  } else {
    head.addEventListener("click", () => focusShow(first));
    head.addEventListener("mouseenter", () => hoverShow(first, true));
    head.addEventListener("mouseleave", () => hoverShow(first, false));
  }
  return li;
}

function setActive(id) {
  document.querySelectorAll("[data-id]").forEach((el) =>
    el.classList.toggle("active", el.dataset.id === id));
}

// two-way sync: hovering a list row previews its marker
function hoverShow(show, on) {
  const m = markerById[show.id];
  if (!m) return;
  if (on) { if (!cluster.hasLayer(m) || map.getZoom() >= 6) m.openTooltip(); }
  else m.closeTooltip();
}

function focusShow(show) {
  const m = markerById[show.id];
  setActive(show.id);
  if (m) {
    map.setView([show.lat, show.lng], Math.max(map.getZoom(), 13), { animate: true });
    cluster.zoomToShowLayer(m, () => m.openPopup());
  }
}

// ---------- Boot ----------
async function boot() {
  try {
    const res = await fetch("data/shows.json", { cache: "no-store" });
    const data = await res.json();
    ALL = data.shows || [];
    const updated = data.meta?.generated_at ? `更新於 ${esc(data.meta.generated_at)} · ` : "";
    els.note.textContent = `${updated}共 ${ALL.length} 部（${data.meta?.verified ?? "?"} 已驗證）`;
  } catch (e) {
    els.note.textContent = "⚠ 無法載入 data/shows.json（需用本機 server 開啟，見 README）";
    console.error(e);
  }
  render();
}

els.search.addEventListener("input", render);
els.search.addEventListener("keydown", (e) => { if (e.key === "Escape") { els.search.value = ""; render(); } });
els.filters.forEach((cb) => cb.addEventListener("change", render));
boot();
