/* ============================================================================
   data2.js — v2 demos only. Loads AFTER data.js, patches REAL poster image URLs
   (+ optional fit hint) onto MM.shows by id. Original data.js untouched so v1
   demos stay byte-identical for comparison.

   Sources (all verified HTTP 200 + image/*):
   • Production MusicalMap CDN (headout/ctfassets/hankyu/interpark) — proper
     480x720 portrait key art, higher-res. Used where available & poster-shaped.
   • Wikipedia infobox art (upload.wikimedia.org — no hotlink block, CORS *,
     loads under <meta referrer no-referrer>) — fills the gaps Spring Awakening /
     Cats / Cabaret / Sweeney Todd / Standing, + a proper portrait Wicked.
   `fit:'contain'` flags logo-style art that must NOT be cover-cropped.
   ========================================================================== */
(function () {
  if (!window.MM) { console.error('data2.js needs data.js first'); return; }
  const H = 'https://cdn-imgix.headout.com/media/images/';
  const C = 'https://images.ctfassets.net/6pezt69ih962/';
  const W = 'https://upload.wikimedia.org/wikipedia/en/';
  const P = {
    1:  {u:H+'0d2f261f-c0e0-4408-b28a-27950a26e991-1778060467801-388152.png'},                                  // Hamilton
    2:  {u:W+'b/b4/Wicked-poster.jpg'},                                                                          // Wicked (portrait)
    3:  {u:C+'47DmmERqPjWVTLnJFvHdU8/2a237f6cef4165a6c73c35d7ae5d68ab/MIS_Updated-Ticket-Agent_480x720_AW.jpg'},  // Les Misérables
    4:  {u:C+'spO4dvQ2d27GnxYWBxnBF/8c5b5f11521a16004fc4c9f8b6a2ec9f/480x720.jpg'},                               // Phantom
    5:  {u:H+'4961cf32-a464-4281-826c-eb62518aae17-1775618329205-373998%20vertical.jpg'},                        // The Lion King
    6:  {u:H+'2a538059-1d74-4a3f-b05f-510603e2e0d1-1775027874101-large-MR_065_Banner_Resizing_2022_heart-portal_v01_480x720.jpg'}, // Moulin Rouge!
    7:  {u:H+'cf43939faa62255f2a620aa384e48cf1-10069.png'},                                                      // Hadestown
    8:  {u:H+'ee361875-e48c-4ed3-9b11-854ddb98f748-1775027715542-250505_SIX_ConcertBanners_480x720_RG3.jpg'},    // Six
    9:  {u:H+'4fff2f87-e48e-4548-8aac-bfbe16e8fa6e-1772689290764-358223.png'},                                   // Aladdin
    10: {u:C+'47DmmERqPjWVTLnJFvHdU8/2a237f6cef4165a6c73c35d7ae5d68ab/MIS_Updated-Ticket-Agent_480x720_AW.jpg'},  // Les Mis (Tokyo)
    11: {u:'https://kageki.hankyu.co.jp/revue/2026/elisabeth/a7ouvb0000107sqo-img/a7ouvb0000107sxw.jpg'},        // Elisabeth (Takarazuka)
    12: {u:W+'b/b4/Wicked-poster.jpg'},                                                                          // Wicked (Seoul)
    13: {u:'https://ticketimage.interpark.com/Play/image/large/26/26007442_p.gif'},                             // Dear Evan Hansen
    14: {u:W+'4/41/Spring_Awakening_2006_album_cover.jpg'},                                                      // Spring Awakening
    15: {u:W+'3/3e/CatsMusicalLogo.jpg', fit:'contain', bg:'#000'},                                             // Cats (logo)
    16: {u:H+'d66afba2-6e75-4846-9341-0b3e36699a05-1775548697541-373817.png'},                                  // Book of Mormon
    17: {u:W+'7/7f/Cabaret_1966_Musical_Poster.jpg'},                                                           // Cabaret
    18: {u:H+'0d2f261f-c0e0-4408-b28a-27950a26e991-1778060467801-388152.png'},                                  // Hamilton (NY)
    19: {u:W+'2/2a/SweeneyToddLogo.jpg', fit:'contain', bg:'#111'},                                             // Sweeney Todd (logo)
    20: {u:H+'4961cf32-a464-4281-826c-eb62518aae17-1775618329205-373998%20vertical.jpg'},                        // König der Löwen = Lion King
    21: {u:W+"c/c4/Standing_at_the_Sky%27s_Edge_West_End_poster.jpg"},                                          // Standing at the Sky's Edge
    22: {u:H+'cf43939faa62255f2a620aa384e48cf1-10069.png'},                                                      // Hadestown (London)
  };
  MM.shows.forEach(s => {
    const p = P[s.id];
    s.poster = p ? p.u : null;
    s.posterFit = p && p.fit ? p.fit : 'cover';
    s.posterBg = p && p.bg ? p.bg : null;
  });
})();
