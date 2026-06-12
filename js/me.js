/* My Musicals — personal log, dashboard & map (Supabase + Chart.js + Leaflet).
 * User content is escaped; the publishable key is public (RLS protects data). */

const cfg = window.MM_CONFIG || {};
const $ = (s) => document.querySelector(s);
const esc = (v) => String(v ?? "").replace(/[&<>"']/g, (c) =>
  ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
// search normalization — must match scrapers/gen_catalog.py _clean(): lowercase,
// fold 臺→台, strip Latin diacritics (madach→Madách) WITHOUT touching CJK/kana/
// Cyrillic, then strip every bracket/quote/separator (half/full-width, CJK, curly).
const SEARCH_PUNCT = /[()\[\]{}（）［］｛｝「」『』【】〔〕《》〈〉<>＜＞"'`＂＇“”‘’｀、・·,，:：/／|｜~～\-－—–]+/g;
const FOLD_EXTRA = { "ł": "l", "ø": "o", "ß": "ss", "đ": "d", "æ": "ae", "œ": "oe", "ı": "i", "ð": "d", "þ": "th" };
function foldLatin(s) {
  let out = "";
  for (const ch of s) {
    if (FOLD_EXTRA[ch]) { out += FOLD_EXTRA[ch]; continue; }
    const d = ch.normalize("NFKD");
    out += (d.charCodeAt(0) < 128 && /[a-z]/.test(d[0])) ? d.replace(/[̀-ͯ]/g, "") : ch;
  }
  return out;
}
const norm = (s) => foldLatin((s || "").toLowerCase().replace(/臺/g, "台")).replace(SEARCH_PUNCT, " ").replace(/\s+/g, " ").trim();

let sb = null;
let CATALOG = { venues: [], cities: [], titles: [], currencies: [], posters: {} };
let POSTER_BY_TITLE = {};   // lowercased en/zh -> poster url
let SIGHTINGS = [];
let map, layer, charts = {};

// ---------- boot ----------
async function boot() {
  CATALOG = await fetch("data/venues_catalog.json").then((r) => r.json()).catch(() => CATALOG);
  (CATALOG.titles || []).forEach((t) => {
    const p = CATALOG.posters[t.group];
    if (!p) return;
    if (t.en) POSTER_BY_TITLE[t.en.toLowerCase()] = p;
    if (t.zh) POSTER_BY_TITLE[t.zh.toLowerCase()] = p;
  });
  if (!cfg.READY) { $("#cfg-warn").hidden = false; }
  else {
    sb = supabase.createClient(cfg.SUPABASE_URL, cfg.SUPABASE_ANON_KEY);
    sb.auth.onAuthStateChange((_e, session) => renderAuth(session));
    renderAuth((await sb.auth.getSession()).data.session);
  }
  wireUi();
}

function renderAuth(session) {
  const user = session?.user;
  $("#signed-in").hidden = !user;
  $("#signed-out").hidden = !!user;
  $("#btn-login").hidden = !!user;
  $("#btn-logout").hidden = !user;
  $("#me-user").textContent = user ? (user.user_metadata?.full_name || user.email) : "";
  if (user) loadSightings();
}

async function login() {
  if (!sb) { alert("Backend not configured yet — see docs/SETUP_ACCOUNTS.md"); return; }
  await sb.auth.signInWithOAuth({ provider: "google", options: { redirectTo: location.origin + location.pathname } });
}

async function loadSightings() {
  const { data, error } = await sb.from("sightings").select("*").order("seen_date", { ascending: false });
  if (error) { console.error(error); return; }
  SIGHTINGS = data || [];
  renderAll();
}

function posterFor(title) {
  return POSTER_BY_TITLE[(title || "").toLowerCase()] || null;
}

// ---------- rendering ----------
function renderAll() { renderTiles(); renderMap(); renderCharts(); renderList(); }
const uniq = (a) => [...new Set(a.filter(Boolean))];
const tile = (n, l) => `<div class="tile"><div class="tn">${n}</div><div class="tl">${l}</div></div>`;

function renderTiles() {
  const s = SIGHTINGS;
  $("#tiles").innerHTML = [
    tile(s.length, "Shows seen"),
    tile(uniq(s.map((x) => x.title)).length, "Musicals"),
    tile(uniq(s.map((x) => x.country)).length, "Countries"),
    tile(uniq(s.map((x) => x.city)).length, "Cities"),
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
       <span class="bv">${v}</span></div>`).join("") : `<p class="muted">No data yet</p>`;
}

function lineChart(id, labels, values) {
  if (charts[id]) charts[id].destroy();
  const white = "#ffffff", grid = "rgba(255,255,255,.25)", tick = "rgba(255,255,255,.9)";
  charts[id] = new Chart($(id), {
    type: "line",
    data: { labels, datasets: [{ data: values, borderColor: white, backgroundColor: "rgba(255,255,255,.22)",
      fill: true, tension: 0.3, pointBackgroundColor: white, pointBorderColor: white, pointRadius: 3, borderWidth: 2.5 }] },
    options: { plugins: { legend: { display: false } },
      scales: {
        y: { beginAtZero: true, ticks: { precision: 0, color: tick }, grid: { color: grid }, border: { color: grid } },
        x: { ticks: { color: tick }, grid: { color: grid }, border: { color: grid } },
      } },
  });
}

function renderCharts() {
  topList("#c-shows", "title");
  topList("#c-countries", "country");
  topList("#c-cities", "city");
  topList("#c-venues", "venue");
  const years = {}, months = Array(12).fill(0), wd = Array(7).fill(0);
  SIGHTINGS.forEach((s) => {
    if (!s.seen_date) return;
    const d = new Date(s.seen_date + "T00:00:00");
    if (isNaN(d)) return;
    years[d.getFullYear()] = (years[d.getFullYear()] || 0) + 1;
    months[d.getMonth()]++; wd[d.getDay()]++;
  });
  const yk = Object.keys(years).sort();
  lineChart("#c-year", yk, yk.map((y) => years[y]));
  lineChart("#c-month", ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], months);
  lineChart("#c-weekday", ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"], wd);
}

function posterIcon(title, img) {
  const p = img || posterFor(title);
  const style = p ? `background-image:url('${esc(p)}')` : "";
  return L.divIcon({
    className: "mm-icon",
    html: `<div class="poster-pin ${p ? "" : "noimg"}" style="${style}">${p ? "" : "<span class='glyph'>♪</span>"}</div>`,
    iconSize: [44, 60], iconAnchor: [22, 60], popupAnchor: [0, -58],
  });
}

// minimum zoom at which one world is at least as wide as the container, so there's
// no empty grey gap beside the map (Leaflet shows void when world < container).
function worldFillZoom() {
  return Math.ceil(Math.log2(Math.max(1, map.getSize().x) / 256));
}
function clampWorld() {
  map.invalidateSize();
  const z = worldFillZoom();
  map.setMinZoom(z);
  if (map.getZoom() < z) map.setView([20, 0], z);
}

function renderMap() {
  if (!map) {
    map = L.map("me-map", { worldCopyJump: true, minZoom: 1, maxBoundsViscosity: 1.0 }).setView([20, 0], 2);
    L.tileLayer("https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png",
      { attribution: "&copy; OpenStreetMap &copy; CARTO", subdomains: "abcd", maxZoom: 19 }).addTo(map);
    layer = L.markerClusterGroup({ showCoverageOnHover: false, maxClusterRadius: 45 });
    map.addLayer(layer);
    map.setMaxBounds([[-85, -180], [85, 180]]);  // keep within one world (no void panning)
    clampWorld();
    window.addEventListener("resize", clampWorld);
  }
  layer.clearLayers();
  const pts = [];
  SIGHTINGS.forEach((s) => {
    if (typeof s.lat !== "number") return;
    const p = posterFor(s.title);
    const m = L.marker([s.lat, s.lng], { icon: posterIcon(s.title), riseOnHover: true }).bindPopup(
      `<div style="display:flex;gap:10px">${p ? `<img src="${esc(p)}" style="width:70px;border-radius:6px">` : ""}
       <div><b>${esc(s.title)}</b><br><span style="color:#666">${esc(s.venue || "")}<br>${esc(s.city || "")}, ${esc(s.country || "")}${s.seen_date ? "<br>" + esc(s.seen_date) : ""}</span></div></div>`,
      { maxWidth: 300 });
    layer.addLayer(m); pts.push([s.lat, s.lng]);
  });
  if (pts.length) map.fitBounds(pts, { padding: [50, 50], maxZoom: 9 });
}

function renderList() {
  $("#log-count").textContent = SIGHTINGS.length ? `(${SIGHTINGS.length})` : "";
  $("#log-list").innerHTML = SIGHTINGS.map((s) => {
    const p = posterFor(s.title);
    const sub = [s.venue, s.city, s.country].filter(Boolean).join(" · ");
    const extra = [s.seat, s.price ? `${s.price}${s.currency ? " " + s.currency : ""}` : ""].filter(Boolean).join(" · ");
    return `<li class="log-item">
      <div class="lthumb ${p ? "" : "noimg"}" style="${p ? `background-image:url('${esc(p)}')` : ""}">${p ? "" : "♪"}</div>
      <div class="li-main">
        <div class="li-title">${esc(s.title)}</div>
        <div class="muted">${esc(s.seen_date || "")}</div>
        <div class="muted">${esc(sub)}</div>
        ${extra ? `<div class="muted">${esc(extra)}</div>` : ""}
      </div>
      <div class="li-acts"><button class="edit" data-id="${s.id}">Edit</button><button class="del" data-id="${s.id}">Delete</button></div>
    </li>`;
  }).join("") || `<li class="muted">No entries yet — click “＋ Add a musical”.</li>`;
  $("#log-list").querySelectorAll(".del").forEach((b) => b.onclick = () => delSighting(b.dataset.id));
  $("#log-list").querySelectorAll(".edit").forEach((b) => b.onclick = () => openEdit(b.dataset.id));
}

async function delSighting(id) {
  if (!confirm("Delete this entry?")) return;
  await sb.from("sightings").delete().eq("id", id);
  loadSightings();
}

// ---------- add / edit ----------
function openAdd() {
  const f = $("#add-form"); f.reset(); f.id.value = "";
  $("#form-title").textContent = "Add a musical";
  $("#add-dialog").showModal();
}
function openEdit(id) {
  const s = SIGHTINGS.find((x) => String(x.id) === String(id));
  if (!s) return;
  const f = $("#add-form"); f.reset();
  ["id", "title", "venue", "city", "country", "seen_date", "seen_time", "seat", "price", "currency", "note"]
    .forEach((k) => { if (f[k]) f[k].value = s[k] ?? ""; });
  $("#form-title").textContent = "Edit musical";
  $("#add-dialog").showModal();
}

async function onSave(e) {
  const f = e.target, g = (n) => (f[n].value.trim() || null);
  const rec = {
    title: g("title"), venue: g("venue"), city: g("city"), country: g("country"),
    seen_date: g("seen_date"), seen_time: g("seen_time"), seat: g("seat"),
    price: g("price"), currency: g("currency"), note: g("note"),
  };
  const v = CATALOG.venues.find((x) => x.name === rec.venue);
  if (v) { rec.lat = v.lat; rec.lng = v.lng; if (!rec.city) rec.city = v.city; if (!rec.country) rec.country = v.country; }
  const id = f.id.value;
  const res = id ? await sb.from("sightings").update(rec).eq("id", id)
                 : await sb.from("sightings").insert(rec);
  if (res.error) { alert("Save failed: " + res.error.message); return; }
  $("#add-dialog").close();
  loadSightings();
}

// ---------- autocomplete (titles bilingual EN/中文, venues, cities, currencies) ----------
function wireUi() {
  $("#btn-login").onclick = login;
  $("#btn-login2").onclick = login;
  $("#btn-logout").onclick = () => sb?.auth.signOut();
  $("#btn-add").onclick = openAdd;
  $("#btn-cancel").onclick = () => $("#add-dialog").close();
  $("#add-form").addEventListener("submit", onSave);
  setupAutocomplete();
}

function setupAutocomplete() {
  const pop = $("#ac-pop");
  document.querySelectorAll("[data-ac]").forEach((inp) => {
    inp.addEventListener("input", () => {
      // Normalize identically to the catalog search blobs: lowercase, 臺→台, and
      // fold away every bracket/quote/punct width & style (（）［］「」＂＇""''…),
      // so any script/variant and with-or-without-brackets all match.
      const q = norm(inp.value);
      if (!q) { pop.hidden = true; return; }
      const kind = inp.dataset.ac;
      const hay = (s) => norm(s).includes(q);
      let items;
      if (kind === "venues") items = CATALOG.venues.filter((v) => hay(v.search || v.name))
        .slice(0, 8).map((v) => ({ label: v.name, sub: [v.city, v.country].filter(Boolean).join(", "), pick: v.name, v }));
      else if (kind === "cities") items = CATALOG.cities.filter((c) => hay(c.city))
        .slice(0, 8).map((c) => ({ label: c.city, sub: c.country, pick: c.city, country: c.country }));
      else if (kind === "currencies") items = CATALOG.currencies.filter((c) => hay(c))
        .slice(0, 8).map((c) => ({ label: c, pick: c.split(" ")[0] }));
      else items = CATALOG.titles.filter((t) => hay(t.search || (t.en + " " + (t.zh || ""))))
        .slice(0, 10).map((t) => ({ label: t.en, sub: t.zh || "", pick: t.en }));
      if (!items.length) { pop.hidden = true; return; }
      pop.innerHTML = items.map((it, i) =>
        `<div class="ac-item" data-i="${i}">${esc(it.label)}${it.sub ? ` <span class="zh">· ${esc(it.sub)}</span>` : ""}</div>`).join("");
      const r = inp.getBoundingClientRect(), fr = $("#add-form").getBoundingClientRect();
      pop.style.left = (r.left - fr.left) + "px";
      pop.style.top = (r.bottom - fr.top + 2) + "px";
      pop.style.width = r.width + "px";
      pop.hidden = false;
      pop.querySelectorAll(".ac-item").forEach((el) => el.onclick = () => {
        const it = items[+el.dataset.i];
        inp.value = it.pick;
        if (kind === "venues" && it.v) {
          if (it.v.city) $("#add-form").city.value = it.v.city;
          if (it.v.country) $("#add-form").country.value = it.v.country;
        } else if (kind === "cities" && it.country) $("#add-form").country.value = it.country;
        pop.hidden = true;
      });
    });
    inp.addEventListener("blur", () => setTimeout(() => { pop.hidden = true; }, 150));
  });
}

boot();
