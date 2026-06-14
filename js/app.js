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
let MAX_MONTHS = 36;                          // slider range; trimmed to the data's latest start (recomputeRange)
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
//   • londontheatre.co.uk ....... Impact or Awin (~10%, best West End rate)
//   • stage-entertainment.de .... German networks (~4-7%)
// (Korea/Hungary/Taiwan/Japan official sources have no public program → passthrough.)
const AFFILIATE = {
  // Impact: tracking domain + account/ad/campaign IDs come from your Impact dashboard.
  // "ticketmaster.": (u) => `https://imp.pxf.io/c/ACCOUNTID/ADID/CAMPAIGNID?u=${encodeURIComponent(u)}`,
  // Partnerize: camref from your ATG/Partnerize dashboard; destination is appended.
  // "atgtickets.com": (u) => `https://prf.hn/click/camref:CAMREF/destination:${encodeURIComponent(u)}`,
  // Awin: mid = merchant id, affid = your publisher id.
  // "londontheatre.co.uk": (u) => `https://www.awin1.com/cread.php?awinmid=MID&awinaffid=AFFID&ued=${encodeURIComponent(u)}`,
};
function affiliateUrl(u) {
  if (!u) return u;
  try {
    const host = new URL(u).hostname;
    for (const key in AFFILIATE) if (host.includes(key)) return AFFILIATE[key](u);
  } catch { /* leave as-is */ }
  return u;   // default: passthrough (no commission program configured yet)
}

// CDN-side thumbnailing: request a small CROPPED square-ish poster for markers
// and list thumbnails. Contentful / imgix / craft.cloud take different params.
// Original full-size images everywhere — no CDN downscaling/compression.
// (User preference: image quality over load speed.)
function thumb(url) {
  return safeUrl(url);
}
function posterFull(url) {
  return safeUrl(url);
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
function overlapsMonth(show) {
  const ms = monthStart(), me = monthEnd();
  const start = show.start_date ? new Date(show.start_date) : null;
  const end = show.end_date ? new Date(show.end_date) : null;
  if (start && start > me) return false;   // run begins after this month
  if (end) {
    if (end < ms) return false;            // run ended before this month
  } else {
    const horizon = new Date(CUR_Y, CUR_M + OPEN_RUN_HORIZON + 1, 0, 23, 59, 59, 999);
    if (ms > horizon) return false;        // open-ended: don't claim a run past the booking horizon
  }
  return true;                             // any overlap → show on the map
}

// ---------- Map ----------
const map = L.map("map", { zoomControl: true, worldCopyJump: true }).setView([42, -40], 3);
// Base layers: light street map (default) + satellite imagery, toggle top-right.
const streets = L.tileLayer("https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png", {
  attribution: "&copy; OpenStreetMap &copy; CARTO",
  subdomains: "abcd", maxZoom: 19,
}).addTo(map);
const satellite = L.tileLayer(
  "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}", {
    attribution: "Tiles &copy; Esri, Maxar, Earthstar Geographics", maxZoom: 19,
  });
L.control.layers({ "地圖": streets, "衛星": satellite }, null, { position: "topright" }).addTo(map);
const cluster = L.markerClusterGroup({
  maxClusterRadius: 45,
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
let ARCH = {};                                // year -> historical runs (lazy-loaded from data/archive/<year>.json)
let ARCH_INDEX = null;                        // data/archive/index.json (which years exist)
const archLoading = {};                       // year -> in-flight fetch promise (dedup)
let markerById = {};
let didFitBounds = false;

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
  ["西語音樂劇", "西語音樂劇", "#ea580c"],
  ["台灣原創", "台灣原創", "#0f766e"],
  ["日本原創", "日本原創", "#db2777"],
  ["韓國原創", "韓國原創", "#7c3aed"],
  ["歐陸原創", "歐陸原創", "#0891b2"],
];
const ACTIVE_TAGS = new Set();   // empty = show every tradition
const TAG_COLOR = Object.fromEntries(TAG_DEFS.map(([t, , c]) => [t, c]));
const tagBadge = (tag) => tag
  ? `<span class="tag-badge" style="--tag-color:${TAG_COLOR[tag] || "#64748b"}">${esc(tag)}</span>`
  : "";

function buildTagFilters() {
  const counts = {};
  for (const s of ALL) counts[s.tag] = (counts[s.tag] || 0) + 1;
  els.tagFilters.innerHTML = "";
  for (const [tag, label, color] of TAG_DEFS) {
    if (!counts[tag]) continue;                 // hide traditions with no shows
    const chip = document.createElement("button");
    chip.type = "button";
    chip.className = "tagchip";
    chip.style.setProperty("--tag-color", color);
    chip.dataset.tag = tag;
    chip.setAttribute("aria-pressed", "false");
    chip.innerHTML = `<span class="tdot"></span>${esc(label)}<span class="tcount">${counts[tag]}</span>`;
    chip.addEventListener("click", () => {
      if (ACTIVE_TAGS.has(tag)) ACTIVE_TAGS.delete(tag);
      else ACTIVE_TAGS.add(tag);
      chip.classList.toggle("on", ACTIVE_TAGS.has(tag));
      chip.setAttribute("aria-pressed", ACTIVE_TAGS.has(tag) ? "true" : "false");
      render();
    });
    els.tagFilters.appendChild(chip);
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
  return t ? `background-image:url('${esc(t)}')` : "";
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

const YEAR_MS = 31557600000;
function fmtDates(show) {
  const s = show.start_date, e = show.end_date;
  // Ticketmaster gives availability dates, not a confirmed run — label honestly.
  if (show.onsale_only) return e ? `售票中至 ${esc(e)}` : "售票中";
  // open-ended long-runner: end is the rolling booking horizon, not a closing date
  if (show.end_rolling) return s ? `自 ${esc(s)} 上演 · 售票至 ${esc(e)}` : `售票至 ${esc(e)}`;
  if (s && e) {
    // long-runners' end_date is just the rolling booking horizon, not a closing
    // date — showing it as a range would read like a closing announcement.
    if (new Date(e) - new Date(s) > 2.5 * YEAR_MS) return `自 ${esc(s)} 上演`;
    return `${esc(s)} – ${esc(e)}`;
  }
  if (s) return `自 ${esc(s)} 上演`;
  if (e) return `演至 ${esc(e)}`;
  return "";
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
  const poster = posterFull(show.image, 400);
  const img = poster ? `<img class="pop-poster" src="${esc(poster)}" alt="">` : "";
  const links = Array.isArray(show.ticket_links) ? show.ticket_links.filter((l) => safeUrl(l.url)) : [];
  let ticket;
  if (links.length > 1) {
    // 官網永遠在售票連結上方；按鈕等寬堆疊對齊
    const row = (label, arr) => arr.length
      ? `<div class="pop-link-group"><span class="pl-label">${label}</span>${arr.map((l) =>
          `<a class="pop-cta sm" href="${esc(affiliateUrl(safeUrl(l.url)))}" target="_blank" rel="noopener">${esc(l.label || l.country)} →</a>`).join("")}</div>`
      : "";
    ticket = row("官網", links.filter((l) => l.kind === "official"))
           + row("售票", links.filter((l) => l.kind !== "official"));
  } else {
    const url = safeUrl(show.ticket_url) || (links[0] && safeUrl(links[0].url));
    const label = show.link_kind === "official" ? "前往官網購票 →" : "前往售票頁 →";
    ticket = url ? `<a class="pop-cta" href="${esc(affiliateUrl(url))}" target="_blank" rel="noopener">${label}</a>` : "";
  }
  const tname = show.tour_name ? show.tour_name.replace(show.title, canonTitle(show)) : "";
  const tourLine = show.type === "tour" && tname ? `<div class="p-row"><b>${esc(tname)}</b></div>` : "";
  const unverified = show.verified ? "" : `<div class="p-row warn">⚠ 未驗證（示範資料）</div>`;
  return `<div class="popup">${img}<div class="pop-body">
      <p class="p-title">${esc(canonTitle(show))}</p>
      ${tagBadge(show.tag)}
      ${tourLine}
      <div class="p-row"><b>${esc(show.venue)}</b></div>
      <div class="p-row">${esc(show.city)}, ${esc(show.country)}</div>
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
  archLoading[y] = fetch(`data/archive/${y}.json`, { cache: "no-store" })
    .then((r) => r.json()).then((d) => { ARCH[y] = d.runs || []; })
    .catch(() => { ARCH[y] = []; });
  return archLoading[y];
}

function ensureArchiveForView() {
  if (monthOffset >= 0) return Promise.resolve();
  const y = monthStart().getFullYear();
  return Promise.all([loadArchiveYear(y), loadArchiveYear(y - 1)]);
}

function visibleShows() {
  const q = els.search.value.trim().toLowerCase();
  return pool().filter((s) => {
    if (!overlapsMonth(s)) return false;
    if (ACTIVE_TAGS.size && !ACTIVE_TAGS.has(s.tag)) return false;
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
  spreadSame(shows);   // fan same-venue shows into a tiny ring so they don't stack
  shows.forEach((s) => {
    if (typeof s.lat !== "number" || typeof s.lng !== "number") return;
    const m = L.marker([s.dlat, s.dlng], { icon: posterMarkerIcon(s), riseOnHover: true })
      .bindPopup(popupHtml(s), {
        maxWidth: Math.min(620, window.innerWidth - 60),  // never wider than the screen
        className: "mm-popup",
      })
      .bindTooltip(tooltipHtml(s), { direction: "top", offset: [0, -68], className: "mm-tip", opacity: 1 });
    // small card never coexists with the big card
    m.on("popupopen", () => m.closeTooltip());
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

  // sidebar — one row per show; a show playing in multiple cities (e.g. Wicked
  // in London + New York) is a single entry you can expand to see each location.
  // Re-rendering (slider drag, search) must NOT collapse what the user expanded.
  const openKeys = new Set(
    [...els.list.querySelectorAll(".show-group.open")].map((el) => el.dataset.gkey));
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
    [...byGroup.entries()]
      .sort((a, b) => displayTitle(a[1]).localeCompare(displayTitle(b[1])))
      .forEach(([k, items]) => {
        const li = showGroupItem(items);
        li.dataset.gkey = k;
        if (openKeys.has(k)) li.classList.add("open");
        els.list.appendChild(li);
      });
  }

  const groups = new Set(shows.map((s) => s.group || s.title)).size;
  const label = isThisMonth() ? "本月上演" : `${selYM()} 上演`;
  els.count.textContent = `${label}：${groups} 部音樂劇 · ${shows.length} 個地點`;

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
        <div class="title">${esc(title)}${badge}${multi ? `<span class="loc-count">${items.length} 地</span>` : ""}</div>
        <div class="meta">${sub}</div>
      </div>
      ${multi ? `<span class="chev">▾</span>` : ""}
    </div>
    ${multi ? `<ul class="sublist">${items.map((s) => `
      <li class="sub-item" data-id="${esc(s.id)}">
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
    const updated = data.meta?.generated_at ? `更新於 ${esc(data.meta.generated_at)}` : "";
    els.note.textContent = `${updated} · 來源：Broadway · West End · 巡演 · 國際 · Ticketmaster`;
  } catch (e) {
    els.note.textContent = "⚠ 無法載入 data/shows.json（需用本機 server 開啟，見 README）";
    console.error(e);
  }
  // historical archive index (enables dragging the timeline into the past)
  if (SHOW_HISTORY) {
    try {
      ARCH_INDEX = await (await fetch("data/archive/index.json", { cache: "no-store" })).json();
    } catch (e) { ARCH_INDEX = null; }   // archive optional — map still works without it
  }
  buildTagFilters();
  recomputeRange();
  render();
}

// Trim the slider to where the data actually goes — the latest show start month
// (+1 month buffer). No point dragging to 2029 when nothing plays past 2028.
function recomputeRange() {
  let maxOff = 1;
  for (const s of ALL) {
    if (!s.start_date) continue;
    const d = new Date(s.start_date);
    const off = (d.getFullYear() - CUR_Y) * 12 + (d.getMonth() - CUR_M);
    if (off > maxOff) maxOff = off;
  }
  MAX_MONTHS = Math.min(Math.max(maxOff + 1, 3), 48);
  els.tRange.max = MAX_MONTHS;
  const d = new Date(CUR_Y, CUR_M + MAX_MONTHS, 1);
  els.tMonth.max = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`;

  // Extend the slider into the PAST as far as the archive goes (Jan of its earliest year).
  if (ARCH_INDEX && ARCH_INDEX.years && Object.keys(ARCH_INDEX.years).length) {
    const earliest = Math.min(...Object.keys(ARCH_INDEX.years).map(Number));
    MIN_MONTHS = (earliest - CUR_Y) * 12 - CUR_M;   // offset to that year's January
    els.tRange.min = MIN_MONTHS;
    els.tMonth.min = `${earliest}-01`;
  }
}

els.search.addEventListener("input", render);
els.search.addEventListener("keydown", (e) => { if (e.key === "Escape") { els.search.value = ""; render(); } });

// ---------- Time bar (month slider + month picker, kept in sync) ----------
// Granularity is one MONTH: dragging selects a month, and any show whose run
// crosses that month appears (see overlapsMonth). No day-level precision.
function setMonth(offset, { fromSlider = false, fromPicker = false } = {}) {
  monthOffset = Math.min(Math.max(offset, MIN_MONTHS), MAX_MONTHS);  // clamp [earliest archive, +MAX_MONTHS]
  if (!fromSlider) els.tRange.value = monthOffset;
  if (!fromPicker) els.tMonth.value = selYM();
  els.tToday.style.visibility = monthOffset === 0 ? "hidden" : "visible";
  // past months read the archive (lazy-loaded) — wait for it, then render
  ensureArchiveForView().then(render);
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
