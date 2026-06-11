/* MusicalMap — v0 frontend
 * Reads data/shows.json and renders an interactive map + synced sidebar.
 * Data layer (scrapers) and presentation layer (this file) are decoupled:
 * anything that produces a valid shows.json will work here unchanged.
 *
 * Security: show data is treated as UNTRUSTED (it will come from scrapers).
 * All text is escaped via esc(); ticket URLs are protocol-whitelisted.
 */

const TODAY = new Date();

// ---------- safety helpers (untrusted scraped data) ----------
function esc(v) {
  return String(v ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}
function safeUrl(u) {
  if (!u) return null;
  try {
    const parsed = new URL(u, location.href);
    return ["http:", "https:"].includes(parsed.protocol) ? parsed.href : null;
  } catch {
    return null;
  }
}

// ---------- "is this show playing right now?" ----------
// A record is currently on if today is within its run.
// end_date === null means open-ended (typical for resident shows).
function isPlayingNow(show, today = TODAY) {
  const start = show.start_date ? new Date(show.start_date) : null;
  const end = show.end_date ? new Date(show.end_date) : null;
  if (start && today < start) return false;          // hasn't opened yet
  if (end && today > end) return false;              // already closed
  return true;
}

// ---------- Map setup ----------
const map = L.map("map", { zoomControl: true, worldCopyJump: true }).setView([30, -20], 3);

L.tileLayer("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png", {
  attribution: "&copy; OpenStreetMap &copy; CARTO",
  subdomains: "abcd",
  maxZoom: 19,
}).addTo(map);

const cluster = L.markerClusterGroup({ maxClusterRadius: 40, spiderfyOnMaxZoom: true });
map.addLayer(cluster);

// ---------- State ----------
let ALL = [];               // all loaded shows
let markerById = {};        // id -> Leaflet marker

const els = {
  list: document.getElementById("show-list"),
  count: document.getElementById("count"),
  search: document.getElementById("search"),
  filters: document.querySelectorAll('#filters input[type="checkbox"]'),
  note: document.getElementById("data-note"),
};

// ---------- Rendering helpers ----------
function coloredIcon(type) {
  const color = type === "tour" ? "#ff6b6b" : "#4ea1ff";
  return L.divIcon({
    className: "mm-marker",
    html: `<span style="display:block;width:16px;height:16px;border-radius:50%;background:${color};border:2px solid #0f1115;box-shadow:0 0 0 2px ${color}55;"></span>`,
    iconSize: [16, 16],
    iconAnchor: [8, 8],
  });
}

function fmtDates(show) {
  if (show.type === "resident") {
    return show.end_date ? `至 ${esc(show.end_date)}` : "常駐演出中";
  }
  return `${esc(show.start_date || "?")} – ${esc(show.end_date || "?")}`;
}

function popupHtml(show) {
  const tag = show.type === "tour" ? "巡演" : "常駐";
  const unverified = show.verified ? "" :
    `<div class="p-row" style="color:#d8b15a">⚠ 未驗證資料（示範用，待 scraper 確認）</div>`;
  const url = safeUrl(show.ticket_url);
  const ticket = url
    ? `<div class="p-row"><a href="${esc(url)}" target="_blank" rel="noopener">訂票連結 →</a></div>` : "";
  const tourLine = show.type === "tour" && show.tour_name
    ? `<div class="p-row"><b>${esc(show.tour_name)}</b></div>` : "";
  return `<div class="popup">
    <span class="p-tag ${esc(show.type)}">${tag}</span>
    <p class="p-title">${esc(show.title)}</p>
    ${tourLine}
    <div class="p-row"><b>${esc(show.venue)}</b></div>
    <div class="p-row">${esc(show.city)}, ${esc(show.country)}</div>
    <div class="p-row">${fmtDates(show)}</div>
    ${ticket}
    ${unverified}
  </div>`;
}

function listItemHtml(show) {
  const badge = show.verified ? "" : `<span class="badge-unverified">未驗證</span>`;
  const sub = show.type === "tour"
    ? `${esc(show.city)} · ${fmtDates(show)}`
    : `${esc(show.venue)} · ${esc(show.city)}`;
  return `<div class="title"><span class="type-dot ${esc(show.type)}"></span>${esc(show.title)}${badge}</div>
          <div class="meta">${sub}</div>`;
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
    if (!isPlayingNow(s)) return false;           // only show what's on right now
    if (!q) return true;
    return (
      s.title.toLowerCase().includes(q) ||
      (s.city || "").toLowerCase().includes(q) ||
      (s.venue || "").toLowerCase().includes(q) ||
      (s.tour_name || "").toLowerCase().includes(q)
    );
  });
}

// ---------- Sync map + list ----------
function render() {
  const shows = visibleShows();

  // markers
  cluster.clearLayers();
  markerById = {};
  shows.forEach((s) => {
    if (typeof s.lat !== "number" || typeof s.lng !== "number") return;
    const m = L.marker([s.lat, s.lng], { icon: coloredIcon(s.type) }).bindPopup(popupHtml(s));
    cluster.addLayer(m);
    markerById[s.id] = m;
  });

  // list
  els.list.innerHTML = "";
  shows.forEach((s) => {
    const li = document.createElement("li");
    li.className = "show-item";
    li.dataset.id = s.id;
    li.innerHTML = listItemHtml(s);
    li.addEventListener("click", () => focusShow(s));
    els.list.appendChild(li);
  });

  els.count.textContent = `目前上演中：${shows.length} 部`;
}

function focusShow(show) {
  const m = markerById[show.id];
  document.querySelectorAll(".show-item").forEach((el) =>
    el.classList.toggle("active", el.dataset.id === show.id));
  if (m) {
    map.setView([show.lat, show.lng], Math.max(map.getZoom(), 12), { animate: true });
    cluster.zoomToShowLayer(m, () => m.openPopup());
  }
}

// ---------- Boot ----------
async function boot() {
  try {
    const res = await fetch("data/shows.json", { cache: "no-store" });
    const data = await res.json();
    ALL = data.shows || [];
    const updated = data.meta?.generated_at ? `更新於 ${data.meta.generated_at} · ` : "";
    els.note.textContent = `${updated}共 ${ALL.length} 筆（${data.meta?.verified ?? "?"} 已驗證）`;
  } catch (e) {
    els.note.textContent = "⚠ 無法載入 data/shows.json（需用本機 server 開啟，見 README）";
    console.error(e);
  }
  render();
}

els.search.addEventListener("input", render);
els.filters.forEach((cb) => cb.addEventListener("change", render));
boot();
