/* Public, read-only "My Musicals" profile — /u.html?u=<handle>.
 * Anyone can view (no login); anon key reads only profiles flagged is_public
 * and their sightings (enforced by Supabase RLS). Rendering mirrors me.js. */

const cfg = window.MM_CONFIG || {};
const $ = (s) => document.querySelector(s);
const esc = (v) => String(v ?? "").replace(/[&<>"']/g, (c) =>
  ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

let CATALOG = { titles: [], posters: {} };
let POSTER_BY_TITLE = {};
let SIGHTINGS = [];
let map, layer, charts = {};

function posterFor(t) { return POSTER_BY_TITLE[(t || "").toLowerCase()] || null; }

// upgrade a stored sighting's venue name to the catalog's current name (matched by
// coordinate), so old records show the latest name (e.g. National Theater →
// National Theater and Concert Hall) everywhere — list, map, Top Theatres.
function distM(a, b, c, d) {
  const R = 6371008.8, p = Math.PI / 180;
  const h = 0.5 - Math.cos((c - a) * p) / 2 + Math.cos(a * p) * Math.cos(c * p) * (1 - Math.cos((d - b) * p)) / 2;
  return 2 * R * Math.asin(Math.sqrt(h));
}
function upgradeVenueNames() {
  const cv = (CATALOG.venues || []).filter((v) => typeof v.lat === "number");
  const current = new Set(cv.map((v) => v.name));
  SIGHTINGS.forEach((s) => {
    if (!s.venue || typeof s.lat !== "number") return;
    if (current.has(s.venue)) return;                 // current catalog name → keep
    const near = cv.filter((v) => distM(s.lat, s.lng, v.lat, v.lng) <= 40);
    if (near.length === 1) s.venue = near[0].name;    // legacy name + only one venue here → upgrade
    // several venues at this coord (sub-halls) → ambiguous, leave as saved
  });
}
const uniq = (a) => [...new Set(a.filter(Boolean))];
const tile = (n, l) => `<div class="tile"><div class="tn">${n}</div><div class="tl">${l}</div></div>`;

function renderTiles() {
  const s = SIGHTINGS;
  $("#tiles").innerHTML = [
    tile(s.length, "Shows seen"), tile(uniq(s.map((x) => x.title)).length, "Musicals"),
    tile(uniq(s.map((x) => x.country)).length, "Countries"), tile(uniq(s.map((x) => x.city)).length, "Cities"),
    tile(uniq(s.map((x) => x.venue)).length, "Theatres"),
  ].join("");
}
function topList(el, field) {
  const counts = {};
  SIGHTINGS.forEach((s) => { if (s[field]) counts[s[field]] = (counts[s[field]] || 0) + 1; });
  const rows = Object.entries(counts).sort((a, b) => b[1] - a[1]).slice(0, 8);
  const max = rows[0]?.[1] || 1;
  $(el).innerHTML = rows.length ? rows.map(([k, v]) =>
    `<div class="bar-row"><span class="bk">${esc(k)}</span>
       <span class="bt"><span class="bf" style="width:${(v / max * 100).toFixed(0)}%"></span></span>
       <span class="bv">${v}</span></div>`).join("") : `<p class="muted">No data</p>`;
}
function lineChart(id, labels, values) {
  if (charts[id]) charts[id].destroy();
  const w = "#ffffff", g = "rgba(255,255,255,.25)", t = "rgba(255,255,255,.9)";
  charts[id] = new Chart($(id), {
    type: "line",
    data: { labels, datasets: [{ data: values, borderColor: w, backgroundColor: "rgba(255,255,255,.22)",
      fill: true, tension: 0.3, pointBackgroundColor: w, pointRadius: 3, borderWidth: 2.5 }] },
    options: { plugins: { legend: { display: false } },
      scales: { y: { beginAtZero: true, ticks: { precision: 0, color: t }, grid: { color: g }, border: { color: g } },
                x: { ticks: { color: t }, grid: { color: g }, border: { color: g } } } },
  });
}
function renderCharts() {
  topList("#c-shows", "title"); topList("#c-countries", "country");
  topList("#c-cities", "city"); topList("#c-venues", "venue");
  const years = {}, months = Array(12).fill(0), wd = Array(7).fill(0);
  SIGHTINGS.forEach((s) => {
    if (!s.seen_date) return;
    const d = new Date(s.seen_date + "T00:00:00");
    if (isNaN(d)) return;
    years[d.getFullYear()] = (years[d.getFullYear()] || 0) + 1; months[d.getMonth()]++; wd[d.getDay()]++;
  });
  const ys = Object.keys(years).map(Number);
  let yk = [];
  if (ys.length) { const lo = Math.min(...ys), hi = Math.max(...ys); for (let y = lo; y <= hi; y++) yk.push(y); }
  lineChart("#c-year", yk, yk.map((y) => years[y] || 0));   // every year in range, gaps = 0
  lineChart("#c-month", ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], months);
  lineChart("#c-weekday", ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"], wd);
}
function posterIcon(title) {
  const p = posterFor(title);
  return L.divIcon({ className: "mm-icon",
    html: `<div class="poster-pin ${p ? "" : "noimg"}" style="${p ? `background-image:url('${esc(p)}')` : ""}">${p ? "" : "<span class='glyph'>♪</span>"}</div>`,
    iconSize: [44, 60], iconAnchor: [22, 60], popupAnchor: [0, -58] });
}
function clampWorld() { if (map) map.invalidateSize(); }
function renderMap() {
  if (!map) {
    map = L.map("me-map", { worldCopyJump: true, minZoom: 2 }).setView([20, 0], 2);
    L.tileLayer("https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png",
      { attribution: "&copy; OpenStreetMap &copy; CARTO", subdomains: "abcd", maxZoom: 19, noWrap: false }).addTo(map);
    // No number-clustering on a personal map: show every sighting from the start.
    // They may overlap when zoomed out — that's fine — and pull apart as you zoom.
    layer = L.layerGroup().addTo(map);
    map.on("zoomend", relayoutStacks);   // re-fan same-venue stacks at each zoom
    window.addEventListener("resize", clampWorld);
  }
  layer.clearLayers();
  buildStacks(SIGHTINGS);
  const pts = [];
  SIGHTINGS.forEach((s) => {
    if (typeof s.lat !== "number") return;
    const p = posterFor(s.title);
    const m = L.marker([s.lat, s.lng], { icon: posterIcon(s.title), riseOnHover: true }).bindPopup(
      `<div style="display:flex;gap:10px">${p ? `<img src="${esc(p)}" style="width:70px;border-radius:6px">` : ""}
       <div><b>${esc(s.title)}</b><br><span style="color:#666">${esc(s.venue || "")}<br>${esc(s.city || "")}, ${esc(s.country || "")}${s.seen_date ? "<br>" + esc(s.seen_date) : ""}</span></div></div>`,
      { maxWidth: 300 });
    s._m = m; layer.addLayer(m); pts.push([s.lat, s.lng]);
  });
  map.invalidateSize();
  if (pts.length && map.getSize().x) map.fitBounds(pts, { padding: [50, 50], maxZoom: 9 });
  relayoutStacks();
}

// Several shows can share one venue's exact coordinate (e.g. three productions at
// 臺中國家歌劇院). We fan each such group around a ring whose radius is
// max(18 px, 38 m): at low zoom the 18 px floor keeps them visibly offset (never a
// 100 % stack) yet starts splitting immediately; as you zoom the 38 m real-world
// size takes over so they end up at their true, fully-separated positions.
// Recomputed on every zoom. The real lat/lng stay on the record (popups, fitBounds).
let STACKS = [];
function buildStacks(list) {
  const g = {};
  list.forEach((s) => {
    if (typeof s.lat !== "number" || typeof s.lng !== "number") return;
    const k = s.lat.toFixed(5) + "," + s.lng.toFixed(5);
    (g[k] = g[k] || []).push(s);
  });
  STACKS = Object.values(g).filter((grp) => grp.length > 1);
}
function relayoutStacks() {
  if (!map) return;
  const z = map.getZoom();
  STACKS.forEach((grp) => {
    const lat = grp[0].lat, lng = grp[0].lng, latr = lat * Math.PI / 180;
    const mpp = 156543.03392 * Math.cos(latr) / Math.pow(2, z);   // metres per pixel
    const rM = Math.max(18 * mpp, 38);                            // ≥18 px, else true 38 m
    const dLat = rM / 111320, dLng = rM / (111320 * Math.cos(latr));
    grp.forEach((s, i) => {
      if (!s._m) return;
      const a = 2 * Math.PI * i / grp.length - Math.PI / 2;
      s._m.setLatLng([lat + dLat * Math.sin(a), lng + dLng * Math.cos(a)]);
    });
  });
}
// ---------- sortable log table ----------
const COLS = [
  { k: "seen_date", label: "Date" }, { k: "title", label: "Musical" },
  { k: "venue", label: "Theatre" }, { k: "city", label: "City" },
  { k: "country", label: "Country" }, { k: "seat", label: "Seat" },
  { k: "price", label: "Price" }, { k: "url", label: "Link" },
];
let sortKey = "seen_date", sortDir = -1;   // default: newest first

function renderTable() {
  const rows = [...SIGHTINGS].sort((a, b) => {
    let x = a[sortKey], y = b[sortKey];
    if (sortKey === "price") { x = +x || 0; y = +y || 0; }
    else { x = (x ?? "").toString().toLowerCase(); y = (y ?? "").toString().toLowerCase(); }
    return x < y ? -sortDir : x > y ? sortDir : 0;
  });
  const head = "<thead><tr>" + COLS.map((c) =>
    `<th data-k="${c.k}" class="${sortKey === c.k ? "sorted " + (sortDir > 0 ? "asc" : "desc") : ""}">${c.label}</th>`).join("") + "</tr></thead>";
  const body = "<tbody>" + (rows.length ? rows.map((s) => "<tr>" + COLS.map((c) => {
    if (c.k === "url") return `<td>${linksOf(s).map((u) => `<a href="${esc(u)}" target="_blank" rel="noopener">🔗</a>`).join(" ")}</td>`;
    if (c.k === "price") return `<td>${s.price != null && s.price !== "" ? esc(s.price) + (s.currency ? " " + esc(s.currency) : "") : ""}</td>`;
    return `<td>${esc(s[c.k] ?? "")}</td>`;
  }).join("") + "</tr>").join("") : `<tr><td colspan="${COLS.length}" class="muted">No entries.</td></tr>`) + "</tbody>";
  const t = $("#log-table");
  t.innerHTML = head + body;
  t.querySelectorAll("th").forEach((th) => th.onclick = () => {
    const k = th.dataset.k;
    if (k === sortKey) sortDir = -sortDir; else { sortKey = k; sortDir = k === "seen_date" ? -1 : 1; }
    renderTable();
  });
}
function safeUrl(u) {
  if (!u) return null;
  try { const p = new URL(u, location.href); return ["http:", "https:"].includes(p.protocol) ? p.href : null; }
  catch { return null; }
}
function linksOf(s) {
  const arr = Array.isArray(s.links) ? s.links : (s.url ? [s.url] : []);
  return arr.map((u) => safeUrl(u)).filter(Boolean);
}
function wireTabs() {
  document.querySelectorAll(".pub-tab").forEach((b) => b.onclick = () => {
    document.querySelectorAll(".pub-tab").forEach((x) => x.classList.toggle("active", x === b));
    const log = b.dataset.tab === "log";
    $("#tab-log").hidden = !log; $("#tab-overview").hidden = log;
    if (!log && map) setTimeout(() => { map.invalidateSize(); clampWorld(); }, 50);
  });
}

async function boot() {
  CATALOG = await fetch("data/venues_catalog.json").then((r) => r.json()).catch(() => CATALOG);
  (CATALOG.titles || []).forEach((t) => {
    const p = CATALOG.posters[t.group]; if (!p) return;
    if (t.en) POSTER_BY_TITLE[t.en.toLowerCase()] = p;
    if (t.zh) POSTER_BY_TITLE[t.zh.toLowerCase()] = p;
  });

  const handle = new URLSearchParams(location.search).get("u");
  if (!cfg.READY || !handle) { $("#pub-empty").hidden = false; return; }
  const sb = supabase.createClient(cfg.SUPABASE_URL, cfg.SUPABASE_ANON_KEY);

  const { data: prof } = await sb.from("profiles")
    .select("id, display_name, is_public").eq("handle", handle).maybeSingle();
  if (!prof || !prof.is_public) { $("#pub-empty").hidden = false; return; }

  const { data: rows } = await sb.from("sightings")
    .select("*").eq("user_id", prof.id).order("seen_date", { ascending: false });
  SIGHTINGS = rows || [];
  upgradeVenueNames();

  document.title = `${prof.display_name || handle} — My Musicals`;
  $("#pub-name").textContent = `${prof.display_name || handle} · My Musicals`;
  $("#pub-sub").textContent = `${SIGHTINGS.length} shows seen worldwide`;
  $("#pub-hero").hidden = false; $("#pub-body").hidden = false;
  wireTabs();
  renderTiles(); renderCharts(); renderTable();
  // defer the map until the just-revealed container has a real size, else fitBounds
  // computes a bad zoom and Leaflet throws (_zoom).
  requestAnimationFrame(() => requestAnimationFrame(renderMap));
}

boot();
