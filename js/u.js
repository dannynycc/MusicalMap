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
  const yk = Object.keys(years).sort();
  lineChart("#c-year", yk, yk.map((y) => years[y]));
  lineChart("#c-month", ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], months);
  lineChart("#c-weekday", ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"], wd);
}
function posterIcon(title) {
  const p = posterFor(title);
  return L.divIcon({ className: "mm-icon",
    html: `<div class="poster-pin ${p ? "" : "noimg"}" style="${p ? `background-image:url('${esc(p)}')` : ""}">${p ? "" : "<span class='glyph'>♪</span>"}</div>`,
    iconSize: [44, 60], iconAnchor: [22, 60], popupAnchor: [0, -58] });
}
function clampWorld() {
  map.invalidateSize();
  const z = Math.ceil(Math.log2(Math.max(1, map.getSize().x) / 256));
  map.setMinZoom(z);
  if (map.getZoom() < z) map.setView([20, 0], z);
}
function renderMap() {
  if (!map) {
    map = L.map("me-map", { worldCopyJump: true, minZoom: 1, maxBoundsViscosity: 1.0 }).setView([20, 0], 2);
    L.tileLayer("https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png",
      { attribution: "&copy; OpenStreetMap &copy; CARTO", subdomains: "abcd", maxZoom: 19 }).addTo(map);
    layer = L.markerClusterGroup({ showCoverageOnHover: false, maxClusterRadius: 45, spiderfyOnMaxZoom: true });
    // markers stacked at one venue (e.g. 3 shows at 臺中國家歌劇院) share exact coords,
    // so zoom-to-bounds can't separate them — spiderfy (fan out) on click instead.
    layer.on("clusterclick", (a) => {
      const ll = a.layer.getAllChildMarkers().map((m) => m.getLatLng());
      if (ll.every((p) => p.equals(ll[0]))) { a.layer.spiderfy(); a.originalEvent?.preventDefault?.(); }
    });
    map.addLayer(layer);
    map.setMaxBounds([[-85, -180], [85, 180]]);
    clampWorld(); window.addEventListener("resize", clampWorld);
  }
  layer.clearLayers();
  const pts = [];
  SIGHTINGS.forEach((s) => {
    if (typeof s.lat !== "number") return;
    const p = posterFor(s.title);
    layer.addLayer(L.marker([s.lat, s.lng], { icon: posterIcon(s.title), riseOnHover: true }).bindPopup(
      `<div style="display:flex;gap:10px">${p ? `<img src="${esc(p)}" style="width:70px;border-radius:6px">` : ""}
       <div><b>${esc(s.title)}</b><br><span style="color:#666">${esc(s.venue || "")}<br>${esc(s.city || "")}, ${esc(s.country || "")}${s.seen_date ? "<br>" + esc(s.seen_date) : ""}</span></div></div>`,
      { maxWidth: 300 }));
    pts.push([s.lat, s.lng]);
  });
  if (pts.length) map.fitBounds(pts, { padding: [50, 50], maxZoom: 9 });
}
function renderList() {
  $("#log-count").textContent = SIGHTINGS.length ? `(${SIGHTINGS.length})` : "";
  $("#log-list").innerHTML = SIGHTINGS.map((s) => {
    const p = posterFor(s.title);
    const sub = [s.venue, s.city, s.country].filter(Boolean).join(" · ");
    return `<li class="log-item">
      <div class="lthumb ${p ? "" : "noimg"}" style="${p ? `background-image:url('${esc(p)}')` : ""}">${p ? "" : "♪"}</div>
      <div class="li-main"><div class="li-title">${esc(s.title)}</div>
        <div class="muted">${esc(s.seen_date || "")}</div><div class="muted">${esc(sub)}</div></div>
    </li>`;
  }).join("") || `<li class="muted">No entries.</li>`;
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

  document.title = `${prof.display_name || handle} — My Musicals`;
  $("#pub-name").textContent = `${prof.display_name || handle} · My Musicals`;
  $("#pub-sub").textContent = `${SIGHTINGS.length} shows seen worldwide`;
  $("#pub-hero").hidden = false; $("#pub-body").hidden = false;
  renderTiles(); renderCharts(); renderMap(); renderList();
}

boot();
