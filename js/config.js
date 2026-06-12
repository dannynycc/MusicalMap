// Supabase config. The publishable key is a PUBLIC key (safe in client code) —
// data is protected by Row Level Security, not by hiding this.
window.MM_CONFIG = {
  SUPABASE_URL: "https://gtuvrhdvwjlvneispcuq.supabase.co",
  SUPABASE_ANON_KEY: "sb_publishable_liJcmr-g9eU9xLLkKixJaA_9s8YjCni",
};
window.MM_CONFIG.READY =
  !window.MM_CONFIG.SUPABASE_URL.startsWith("PASTE") &&
  !window.MM_CONFIG.SUPABASE_ANON_KEY.startsWith("PASTE");
