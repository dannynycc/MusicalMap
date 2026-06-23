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
window.MM_CONFIG.AFFILIATE = {
  // ✅ live
  "ticketmaster.":       { net: "impact", domain: "ticketmaster.evyy.net", ids: "7408739/264167/4272" },
  // 🔜 dormant — fill after approval (apply from the brand's own affiliate page;
  //    cold marketplace requests get rejected — Ticketmaster only approved brand-initiated)
  // TodayTix DIRECT program is closed (FlexOffers "not offering"; hello.todaytix.com dead).
  // LIVE path = Sovrn Commerce: Merchant Explorer (commerce.sovrn.com) lists TodayTix as
  // "Open" (auto-approve). Join Sovrn → paste its link template (a {url} deep link) here.
  "todaytix.com":        { net: "tmpl", tmpl: "https://redirect.viglink.com?key=292f569ccdbe689fdda4735e1b0db677&u={url}" }, // ✅ TodayTix via Sovrn Commerce (VigLink Redirect API; key is public, appears in every link)
  "londontheatre.co.uk": { net: "tmpl", tmpl: "" },               // TodayTix Group — check Sovrn / its own network when applying
  "atgtickets.":         { net: "partnerize", camref: "" },        // ATG / LOVEtheatre — Partnerize (VERIFIED active): signup.partnerize.com/signup/en/ambassadortheatregroup
  "broadwaydirect.com":  { net: "awin", mid: "28987", affid: "" }, // Broadway Direct — Awin merchant 28987 (VERIFIED exists; Nederlander)
};
// Primary-link preference when a show has several ticket links (higher commission
// first). Used by the link-priority layer (Phase 2). Host-substring order.
window.MM_CONFIG.AFFILIATE_PRIORITY = [
  "todaytix.com", "londontheatre.co.uk", "atgtickets.", "broadwaydirect.com", "ticketmaster.",
];
