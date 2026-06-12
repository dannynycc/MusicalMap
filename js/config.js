// Supabase config. The anon key is a PUBLIC key (safe in client code) — data is
// protected by Row Level Security, not by hiding this. Paste your two values:
//   Project Settings → API → Project URL  and  anon public key.
window.MM_CONFIG = {
  SUPABASE_URL: "PASTE_YOUR_PROJECT_URL",     // e.g. https://abcd.supabase.co
  SUPABASE_ANON_KEY: "PASTE_YOUR_ANON_KEY",
};
window.MM_CONFIG.READY =
  !window.MM_CONFIG.SUPABASE_URL.startsWith("PASTE") &&
  !window.MM_CONFIG.SUPABASE_ANON_KEY.startsWith("PASTE");
