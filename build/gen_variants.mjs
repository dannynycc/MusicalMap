// Build-time generator of per-language data variants for the tri-URL site
// (/en/, /zh-hans/, /zh-hant/). Run from repo root: `node build/gen_variants.mjs`.
//
// Why build-time (not client-side): AI crawlers (GPTBot/ClaudeBot/PerplexityBot) do
// NOT run JS, and Google wants distinct URLs per language. So each variant's text is
// baked at build time. OpenCC handles 簡⇄繁 (correct phrase/one-to-many conversion);
// CN/TW/JP/KR place names come from data/i18n_maps.json; a few platform names get
// English labels. Latin text is untouched by OpenCC, so English shows pass through.
import fs from "fs";
import * as OpenCC from "opencc-js";

const cn2tw = OpenCC.Converter({ from: "cn", to: "tw" }); // Simplified → Traditional
const tw2cn = OpenCC.Converter({ from: "tw", to: "cn" }); // Traditional → Simplified
const maps = JSON.parse(fs.readFileSync("data/i18n_maps.json", "utf8"));
const venuesEn = JSON.parse(fs.readFileSync("data/venues_en.json", "utf8")); // official English names for CN/JP/KR/TW theatres
const VARIANTS = ["en", "zh-hans", "zh-hant"];

// City/country localization, language-specific (per user spec):
//   • English: city + US-state / CA-province code. Sources are inconsistent — some give
//     "Boston, MA", some bare "Boston" — so we NORMALISE by back-filling the missing code
//     from CITY_STATE (learned from the records that DO carry one); English is uniformly
//     "City, ST" where a code is known.
//   • Chinese (zh-hant/zh-hans): NO state — just the city, translated for major world cities
//     (data/i18n_maps.json); unmapped places (East Lansing…) stay in their Latin name.
function place(kind, val, variant, rec) {
  if (kind !== "cities" || !val) {
    if (variant === "en") return val;
    const tw = maps[kind + "_tw"];               // Taiwan override (countries_tw) where it differs
    if (variant === "zh-hant" && tw && tw[val]) return tw[val];
    const h = maps[kind][val];
    return h ? (variant === "zh-hant" ? cn2tw(h) : h) : val;
  }
  const m = val.match(/^(.*?),\s*([A-Z]{2})$/);
  const bare = m ? m[1].trim() : val;
  if (variant === "en") {
    const st = m ? m[2] : stateFor(bare, rec);
    return st ? `${bare}, ${st}` : bare;
  }
  // 中文變體:源頭中文城名(city_cn)最權威,優先於拼音對照表——拼音會撞城
  // (江蘇泰州/浙江台州都是 Taizhou,查表把泰州演出標成「台州」;2026-07-14 深稽核)。
  if (rec && rec.city_cn) return variant === "zh-hant" ? cn2tw(rec.city_cn) : rec.city_cn;
  if (variant === "zh-hant" && maps.cities_tw[bare]) return maps.cities_tw[bare];
  const hans = maps.cities[bare];
  return hans ? (variant === "zh-hant" ? cn2tw(hans) : hans) : bare;
}
// Free Chinese text (titles, venues, tour names): convert in both directions so a
// mixed source (Simplified from CN sources, Traditional from TW) lands consistently.
function cjk(val, variant) {
  if (!val) return val;
  if (variant === "zh-hant") return cn2tw(val);
  if (variant === "zh-hans") return tw2cn(val);
  return val; // en: leave as-is
}
// Ticket platform labels: English names for a few; otherwise treat as Chinese text.
function label(val, variant) {
  if (variant === "en" && maps.platforms_en[val]) return maps.platforms_en[val];
  return cjk(val, variant);
}

const src = JSON.parse(fs.readFileSync("data/shows.json", "utf8"));
fs.mkdirSync("data/variants", { recursive: true });

// Learn each US/CA city's state/province code from the records that carry one, so English
// can back-fill it onto bare-named duplicates ("Boston" → "Boston, MA").
// 座標感知(2026-07-14 深稽核):美國同名城會撞名——Wilmington NC 的 6 場曾因唯一帶碼筆
// 是 Wilmington, DE 而全標成 DE(相距 640km);Bloomington IL 標成 IN 同病。所以:
//  • 學到的州碼帶座標,回填時要求同名且座標相近(<0.7°)才用;
//  • 同名帶碼筆存在但座標都遠 = 已證實同名多城 → 不冒充,顯示裸名(寧缺勿錯);
//  • 完全無帶碼筆才 fallback 到人工靜態表 us_ca_state。
const CITY_STATE = [];
for (const s of src.shows) {
  const m = (s.city || "").match(/^(.*?),\s*([A-Z]{2})$/);
  if (m && typeof s.lat === "number") CITY_STATE.push({ city: m[1].trim(), lat: s.lat, lng: s.lng, st: m[2] });
}
function stateFor(bare, rec) {
  const cands = CITY_STATE.filter((c) => c.city === bare);
  if (!cands.length) return maps.us_ca_state[bare] || null;
  if (!rec || typeof rec.lat !== "number") return null;
  const near = cands.find((c) => Math.abs(c.lat - rec.lat) < 0.7 && Math.abs(c.lng - rec.lng) < 0.7);
  return near ? near.st : null;
}

// Search is LANGUAGE-AGNOSTIC (display variant is only for presentation): the blob
// holds every field rendered in ALL THREE forms — English + Traditional + Simplified —
// so e.g. in 繁中 mode "taipei" / "台北" / "臺北" all find 臺北 shows. Same blob across
// every variant file. Built from the original source values (before per-variant mutation).
// Official Chinese display titles per group (show_titles=简 / show_titles_tw=繁;
// 台陸譯名可不同:歌劇魅影 vs 剧院魅影)。只收有官方依據的名字,缺的照舊顯示英文。
const ST_CN = maps.show_titles || {};
const ST_TW = maps.show_titles_tw || {};
function zhTitle(s, variant) {
  if (variant === "zh-hant" && ST_TW[s.group]) return ST_TW[s.group];
  if (variant === "zh-hans" && ST_CN[s.group]) return ST_CN[s.group];
  return null;
}

function buildSearch(s) {
  const parts = new Set();
  if (ST_TW[s.group]) parts.add(ST_TW[s.group]);
  if (ST_CN[s.group]) parts.add(ST_CN[s.group]);
  for (const v of VARIANTS) {
    parts.add(place("cities", s.city, v, s));
    parts.add(place("countries", s.country, v));
    parts.add(cjk(s.title, v));
    if (s.venue) parts.add(v === "en" && venuesEn[s.venue] ? venuesEn[s.venue] : cjk(s.venue, v));
    if (s.tour_name) parts.add(cjk(s.tour_name, v));
  }
  if (s.alt) parts.add(s.alt);
  return [...parts].filter(Boolean).join(" ");
}
const searchBlobs = src.shows.map(buildSearch);

for (const variant of VARIANTS) {
  const out = JSON.parse(JSON.stringify(src));
  out.shows.forEach((s, i) => {
    s.city = place("cities", s.city, variant, s);
    s.country = place("countries", s.country, variant);
    s.title = zhTitle(s, variant) || cjk(s.title, variant);
    if (s.venue) s.venue = (variant === "en" && venuesEn[s.venue]) ? venuesEn[s.venue] : cjk(s.venue, variant);
    if (s.tour_name) s.tour_name = cjk(s.tour_name, variant);
    if (Array.isArray(s.ticket_links)) {
      for (const l of s.ticket_links) if (l.label) l.label = label(l.label, variant);
    }
    s.search = searchBlobs[i];
  });
  out.meta = { ...(out.meta || {}), variant };
  fs.writeFileSync(`data/variants/shows.${variant}.json`, JSON.stringify(out));
  console.log(`${variant.padEnd(8)} → ${out.shows.length} shows`);
}
console.log("done → data/variants/");
