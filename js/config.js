// Supabase config. The publishable key is a PUBLIC key (safe in client code) —
// data is protected by Row Level Security, not by hiding this.
window.MM_CONFIG = {
  SUPABASE_URL: "https://gtuvrhdvwjlvneispcuq.supabase.co",
  SUPABASE_ANON_KEY: "sb_publishable_liJcmr-g9eU9xLLkKixJaA_9s8YjCni",
};
window.MM_CONFIG.READY =
  !window.MM_CONFIG.SUPABASE_URL.startsWith("PASTE") &&
  !window.MM_CONFIG.SUPABASE_ANON_KEY.startsWith("PASTE");

// Affiliate programs. IDs are PUBLIC (they appear in every outbound ticket link —
// there is no secret here). Each entry is keyed by an outbound-host substring and is
// DORMANT until its credentials are filled in — missing creds → plain passthrough
// (no commission, link still works). app.js wraps the matching outbound URL at render
// time only, so the data layer stays clean (raw URLs) and changing an ID is a one-line
// edit here — never a re-scrape. Apply from each BRAND's own affiliate page (cold
// marketplace requests get rejected — Ticketmaster only approved when brand-initiated).
//
// Networks & link formats:
//   impact     : https://{domain}/c/{ids}?u={dest}&subId1={SUBID}   (domain+ids from Impact "Create a link")
//   partnerize : https://prf.hn/click/camref:{camref}/destination:{dest}
//   awin       : https://www.awin1.com/cread.php?awinmid={mid}&awinaffid={affid}&ued={dest}
//   tmpl       : paste the network's own deep-link template with a {url} placeholder
//                (for networks whose exact format we only learn after approval, e.g.
//                 FlexOffers). e.g. "https://track.flexlinkspro.com/a.ashx?foid=…&url={url}"
window.MM_CONFIG.AFFILIATE_SUBID = "musicalmap";   // tags our traffic in dashboards
// Sovrn Commerce / VigLink Redirect API — ONE site key monetizes ANY merchant Sovrn
// is in-network for (out-of-network just passes through, no harm). key is PUBLIC (it
// appears in every outbound link). Verified: redirect.viglink.com?key=…&u=<dest> 302s
// to the destination. NOTE: earnings only start after Sovrn approves the site (Settings
// → Pending, ~3-5 business days after first clicks). `sovrn.co` is the newer equivalent
// domain (same params); redirect.viglink.com still works, so we keep it (verified).
const SOVRN = "https://redirect.viglink.com?key=292f569ccdbe689fdda4735e1b0db677&u={url}";
window.MM_CONFIG.AFFILIATE = {
  // ✅ DIRECT programs (higher commission, full control) — keep these out of Sovrn:
  "ticketmaster.":       { net: "impact", domain: "ticketmaster.evyy.net", ids: "7408739/264167/4272" },
  // ✅ Sovrn catch-all (live once site approved) — every commercial ticketer we link to:
  "todaytix.com":            { net: "tmpl", tmpl: SOVRN },   // TodayTix (direct program closed → Sovrn; merchant 122507 Open, 1-2% CPA+CPC)
  "londontheatre.co.uk":     { net: "tmpl", tmpl: SOVRN },   // TodayTix Group
  "broadway-show-tickets.com":{ net: "tmpl", tmpl: SOVRN },  // Broadway show tickets reseller
  "atgtickets.":             { net: "tmpl", tmpl: SOVRN },   // ATG — interim Sovrn; UPGRADE to Partnerize (higher) when camref arrives: signup.partnerize.com/signup/en/ambassadortheatregroup
  // 🔜 direct upgrade when approved (replace the Sovrn entry above with these):
  //   atgtickets.  → { net:"partnerize", camref:"<camref>" }
  //   broadwaydirect.com → { net:"awin", mid:"28987", affid:"<affid>" }  (no current outbound links yet)
};
// Primary-link preference when a show has several ticket links (higher commission
// first). Used by the link-priority layer (Phase 2). Host-substring order.
window.MM_CONFIG.AFFILIATE_PRIORITY = [
  "todaytix.com", "londontheatre.co.uk", "atgtickets.", "broadwaydirect.com", "ticketmaster.",
];
