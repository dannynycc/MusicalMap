/* My Musicals — personal log, dashboard & map (Supabase + Chart.js + Leaflet).
 * All user content is escaped; the anon key is public (RLS protects data). */

const cfg = window.MM_CONFIG || {};
const $ = (s) => document.querySelector(s);
const esc = (v) => String(v ?? "").replace(/[&<>"']/g, (c) =>
  ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

let sb = null;
let CATALOG = { venues: [], cities: [], titles: [] };
let SIGHTINGS = [];
let map, layer;

// ---------- boot ----------
async function boot() {
  CATALOG = await fetch("data/venues_catalog.json").then((r) => r.json()).catch(() => CATALOG);
  if (!cfg.READY) { $("#cfg-warn").hidden = false; }
  else {
    sb = supabase.createClient(cfg.SUPABASE_URL, cfg.SUPABASE_ANON_KEY);
    sb.auth.onAuthStateChange((_e, session) => renderAuth(session));
    const { data } = await sb.auth.getSession();
    renderAuth(data.session);
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
  if (!sb) { alert("後端尚未設定，見 docs/SETUP_ACCOUNTS.md"); return; }
  await sb.auth.signInWithOAuth({
    provider: "google",
    options: { redirectTo: location.origin + location.pathname },
  });
}

// ---------- data ----------
async function loadSightings() {
  const { data, error } = await sb.from("sightings").select("*").order("seen_date", { ascending: false });
  if (error) { console.error(error); return; }
  SIGHTINGS = data || [];
  renderAll();
}

// ---------- rendering ----------
function renderAll() {
  renderTiles(); renderMap(); renderList(); renderCharts();
}

function uniq(arr) { return [...new Set(arr.filter(Boolean))]; }
function tile(n, label) { return `<div class="tile"><div class="tn">${n}</div><div class="tl">${label}</div></div>`; }

function renderTiles() {
  const s = SIGHTINGS;
  $("#tiles").innerHTML = [
    tile(s.length, "場次"),
    tile(uniq(s.map((x) => x.title)).length, "不同劇目"),
    tile(uniq(s.map((x) => x.country)).length, "國家"),
    tile(uniq(s.map((x) => x.city)).length, "城市"),
    tile(uniq(s.map((x) => x.venue)).length, "劇院"),
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
       <span class="bv">${v}</span></div>`).join("") : `<p class="muted">尚無資料</p>`;
}

let charts = {};
function barChart(id, labels, values) {
  if (charts[id]) charts[id].destroy();
  charts[id] = new Chart($(id), {
    type: "bar",
    data: { labels, datasets: [{ data: values, backgroundColor: "#0f766e", borderRadius: 4 }] },
    options: { plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, ticks: { precision: 0 } } } },
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
  barChart("#c-year", yk, yk.map((y) => years[y]));
  barChart("#c-month", ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"], months);
  barChart("#c-weekday", ["日", "一", "二", "三", "四", "五", "六"], wd);
}

function renderMap() {
  if (!map) {
    map = L.map("me-map", { worldCopyJump: true }).setView([25, 60], 2);
    L.tileLayer("https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png",
      { attribution: "&copy; OpenStreetMap &copy; CARTO", subdomains: "abcd", maxZoom: 19 }).addTo(map);
    layer = L.markerClusterGroup({ showCoverageOnHover: false });
    map.addLayer(layer);
  }
  layer.clearLayers();
  const pts = [];
  SIGHTINGS.forEach((s) => {
    if (typeof s.lat !== "number") return;
    const m = L.marker([s.lat, s.lng]).bindPopup(
      `<b>${esc(s.title)}</b><br>${esc(s.venue || "")}<br>${esc(s.city || "")}, ${esc(s.country || "")}` +
      (s.seen_date ? `<br>${esc(s.seen_date)}` : ""));
    layer.addLayer(m); pts.push([s.lat, s.lng]);
  });
  if (pts.length) map.fitBounds(pts, { padding: [50, 50], maxZoom: 9 });
}

function renderList() {
  $("#log-count").textContent = `（${SIGHTINGS.length}）`;
  $("#log-list").innerHTML = SIGHTINGS.map((s) => `
    <li class="log-item">
      <div><b>${esc(s.title)}</b> <span class="muted">${esc(s.seen_date || "")}</span></div>
      <div class="muted">${esc([s.venue, s.city, s.country].filter(Boolean).join(" · "))}${s.seat ? " · " + esc(s.seat) : ""}${s.price ? ` · ${esc(s.price)}${esc(s.currency || "")}` : ""}</div>
      <button class="del" data-id="${s.id}">刪除</button>
    </li>`).join("") || `<li class="muted">還沒有紀錄，點「＋ 記錄一場音樂劇」開始。</li>`;
  $("#log-list").querySelectorAll(".del").forEach((b) =>
    b.addEventListener("click", () => delSighting(b.dataset.id)));
}

async function delSighting(id) {
  if (!confirm("刪除這筆紀錄？")) return;
  await sb.from("sightings").delete().eq("id", id);
  loadSightings();
}

// ---------- add form + autocomplete ----------
function wireUi() {
  $("#btn-login").onclick = login;
  $("#btn-login2").onclick = login;
  $("#btn-logout").onclick = () => sb?.auth.signOut();
  $("#btn-add").onclick = () => { $("#add-form").reset(); $("#add-dialog").showModal(); };
  $("#btn-cancel").onclick = () => $("#add-dialog").close();
  $("#add-form").addEventListener("submit", onSave);
  setupAutocomplete();
}

async function onSave(e) {
  const f = e.target;
  const g = (n) => f[n].value.trim() || null;
  const rec = {
    title: g("title"), venue: g("venue"), city: g("city"), country: g("country"),
    seen_date: g("seen_date"), seen_time: g("seen_time"), seat: g("seat"),
    price: g("price"), currency: g("currency"), note: g("note"),
  };
  const v = CATALOG.venues.find((x) => x.name === rec.venue);
  if (v) { rec.lat = v.lat; rec.lng = v.lng; }
  const { error } = await sb.from("sightings").insert(rec);
  if (error) { alert("儲存失敗：" + error.message); return; }
  $("#add-dialog").close();
  loadSightings();
}

function setupAutocomplete() {
  const pop = $("#ac-pop");
  let active = null;
  document.querySelectorAll("[data-ac]").forEach((inp) => {
    inp.addEventListener("input", () => {
      active = inp;
      const q = inp.value.trim().toLowerCase();
      if (!q) { pop.hidden = true; return; }
      const kind = inp.dataset.ac;
      let items = [];
      if (kind === "venues") items = CATALOG.venues.filter((v) => v.name.toLowerCase().includes(q)).slice(0, 8);
      else if (kind === "cities") items = CATALOG.cities.filter((c) => c.city.toLowerCase().includes(q)).slice(0, 8);
      else items = CATALOG.titles.filter((t) => t.toLowerCase().includes(q)).slice(0, 8).map((t) => ({ name: t }));
      if (!items.length) { pop.hidden = true; return; }
      pop.innerHTML = items.map((it, i) =>
        `<div class="ac-item" data-i="${i}">${esc(it.name || it.city)}${it.city && it.name ? `<span class="muted"> · ${esc(it.city)}</span>` : it.country ? `<span class="muted"> · ${esc(it.country)}</span>` : ""}</div>`).join("");
      const r = inp.getBoundingClientRect(), fr = $("#add-form").getBoundingClientRect();
      pop.style.left = (r.left - fr.left) + "px";
      pop.style.top = (r.bottom - fr.top + 2) + "px";
      pop.style.width = r.width + "px";
      pop.hidden = false;
      pop.querySelectorAll(".ac-item").forEach((el) => el.onclick = () => {
        const it = items[+el.dataset.i];
        if (kind === "venues") {
          active.value = it.name;
          if (it.city) $("#add-form").city.value = it.city;
          if (it.country) $("#add-form").country.value = it.country;
        } else if (kind === "cities") {
          active.value = it.city;
          if (it.country) $("#add-form").country.value = it.country;
        } else active.value = it.name;
        pop.hidden = true;
      });
    });
    inp.addEventListener("blur", () => setTimeout(() => { pop.hidden = true; }, 150));
  });
}

boot();
