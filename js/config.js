// Supabase config. The publishable key is a PUBLIC key (safe in client code) —
// data is protected by Row Level Security, not by hiding this.
window.MM_CONFIG = {
  SUPABASE_URL: "https://gtuvrhdvwjlvneispcuq.supabase.co",
  SUPABASE_ANON_KEY: "sb_publishable_liJcmr-g9eU9xLLkKixJaA_9s8YjCni",
};
window.MM_CONFIG.READY =
  !window.MM_CONFIG.SUPABASE_URL.startsWith("PASTE") &&
  !window.MM_CONFIG.SUPABASE_ANON_KEY.startsWith("PASTE");

// Affiliate tracking (impact.com). These IDs are PUBLIC — they appear in every
// outbound ticket link, there is no secret here. Taken from Impact's "Create a link"
// tool, e.g.  https://ticketmaster.evyy.net/c/7408739/264167/4272?u=<destination>
// app.js wraps any Ticketmaster ticket URL as  <prefix>?u=<encoded show page>&subId1=<SUBID>
// so the buyer still lands on the SAME show page, now with our commission tracking.
// To turn it off, set TICKETMASTER to null (links fall back to plain passthrough).
window.MM_CONFIG.IMPACT = {
  TICKETMASTER: { domain: "ticketmaster.evyy.net", account: "7408739", campaign: "264167", ad: "4272" },
  SUBID: "musicalmap",   // tags our traffic so it's identifiable in the Impact dashboard
};
