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

// City/country: English in data → localized only for CN/TW/JP/KR (others stay English).
function place(kind, val, variant) {
  if (variant === "en") return val;
  const hans = maps[kind][val];
  if (!hans) return val; // New York, London… not localized
  return variant === "zh-hant" ? cn2tw(hans) : hans;
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
