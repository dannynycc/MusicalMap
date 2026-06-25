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
const VARIANTS = ["en", "zh-hans", "zh-hant"];

// City/country localization, language-specific (per user spec):
//   • English: city + US-state / CA-province code. Sources are inconsistent — some give
//     "Boston, MA", some bare "Boston" — so we NORMALISE by back-filling the missing code
//     from CITY_STATE (learned from the records that DO carry one); English is uniformly
//     "City, ST" where a code is known.
//   • Chinese (zh-hant/zh-hans): NO state — just the city, translated for major world cities
//     (data/i18n_maps.json); unmapped places (East Lansing…) stay in their Latin name.
function place(kind, val, variant) {
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
    const st = m ? m[2] : (CITY_STATE[bare] || maps.us_ca_state[bare]);
    return st ? `${bare}, ${st}` : bare;
  }
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
const CITY_STATE = {};
for (const s of src.shows) {
  const m = (s.city || "").match(/^(.*?),\s*([A-Z]{2})$/);
  if (m) CITY_STATE[m[1].trim()] = m[2];
}

for (const variant of VARIANTS) {
  const out = JSON.parse(JSON.stringify(src));
  for (const s of out.shows) {
    s.city = place("cities", s.city, variant);
    s.country = place("countries", s.country, variant);
    s.title = cjk(s.title, variant);
    if (s.venue) s.venue = cjk(s.venue, variant);
    if (s.tour_name) s.tour_name = cjk(s.tour_name, variant);
    if (Array.isArray(s.ticket_links)) {
      for (const l of s.ticket_links) if (l.label) l.label = label(l.label, variant);
    }
  }
  out.meta = { ...(out.meta || {}), variant };
  fs.writeFileSync(`data/variants/shows.${variant}.json`, JSON.stringify(out));
  console.log(`${variant.padEnd(8)} → ${out.shows.length} shows`);
}
console.log("done → data/variants/");
