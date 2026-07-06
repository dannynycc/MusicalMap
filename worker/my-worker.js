/* Cloudflare Worker — my.themusicalmap.com/<handle> 個人公開頁
   (docs/DESIGN_username_sharing.md 網址層實作;部署步驟見 docs/SETUP_MY_SUBDOMAIN.md)

   做三件事:
   1. 乾淨網址:/<handle> 內部改寫成 GitHub Pages 的 u.html(注入 window.MM_HANDLE,前端照常跑)。
   2. 舊名 301:handle 查無 → resolve_handle(舊名→現用名)→ 301 到新網址(alias 永久有效)。
   3. 爬蟲可見:回傳前注入該使用者專屬 <title>/description/og/canonical/JSON-LD
      (u.html 原本純前端 render,爬蟲/AI 什麼都看不到;這層補上,對標 flightradar24 個人頁)。

   資安:此處只用公開 anon key + 只讀公開資料(profiles 的 RLS 只放行 is_public;
   resolve_handle 只回公開帳號)。無任何秘密,程式碼可公開。 */

const GH_ORIGIN = 'https://themusicalmap.com';   // 主站來源(2026-07-06 已遷移至自訂網域)
const MAIN_SITE = 'https://themusicalmap.com';
const SUPABASE_URL = 'https://gtuvrhdvwjlvneispcuq.supabase.co';
const ANON_KEY = 'sb_publishable_liJcmr-g9eU9xLLkKixJaA_9s8YjCni';   // 公開 key(RLS 把關)

// 與 DB handle_reserved()、me.html RESERVED 同步(supabase/add_handle_aliases.sql)
const RESERVED = new Set(['u','me','index','admin','api','app','www','my','null','undefined',
  'theatres','privacy','terms','login','logout','signup','settings','account','stats','static',
  'assets','js','css','data','posters','logos','en','zh-hant','zh-hans','help','about','official','map','share']);

const esc = (s) => String(s ?? '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');

async function sbGet(path) {
  const r = await fetch(SUPABASE_URL + path, { headers: { apikey: ANON_KEY } });
  return r.ok ? r.json() : null;
}
async function sbRpc(fn, args) {
  const r = await fetch(`${SUPABASE_URL}/rest/v1/rpc/${fn}`, {
    method: 'POST',
    headers: { apikey: ANON_KEY, 'Content-Type': 'application/json' },
    body: JSON.stringify(args),
  });
  return r.ok ? r.json() : null;
}

export default {
  async fetch(req) {
    const url = new URL(req.url);
    const path = url.pathname;

    // robots:my. 子網域自己的(全放行;個人頁本來就要被索引)
    if (path === '/robots.txt') {
      return new Response('User-agent: *\nAllow: /\n', { headers: { 'content-type': 'text/plain' } });
    }
    // 根 → 主站
    if (path === '/' || path === '') return Response.redirect(MAIN_SITE, 302);

    const seg = path.replace(/^\/+|\/+$/g, '');
    // 含 . 或 / 的是靜態資源(css/js/data/posters/圖檔) → 直接代理 GitHub Pages
    if (seg.includes('.') || seg.includes('/')) {
      return fetch(GH_ORIGIN + path + url.search);
    }
    // 保留字不是 handle → 丟回主站對應頁(或首頁)
    if (RESERVED.has(seg.toLowerCase())) return Response.redirect(MAIN_SITE, 302);

    // 尾斜線正規化(相對路徑解析需要 /danny 而非 /danny/)
    if (path.endsWith('/')) return Response.redirect(url.origin + '/' + seg, 301);

    const handle = seg.toLowerCase();

    // 1) 查現用 handle(RLS:只回公開帳號 → 私密帳號自然走 not-found,不洩漏存在性)
    const profs = await sbGet(`/rest/v1/profiles?select=display_name,is_public&handle=eq.${encodeURIComponent(handle)}&limit=1`);
    const prof = profs && profs[0];

    // 2) 查無 → 舊名?301 到現用名(alias 永久有效)
    if (!prof || !prof.is_public) {
      const nh = await sbRpc('resolve_handle', { p_handle: handle });
      if (nh && nh !== handle) return Response.redirect(url.origin + '/' + nh, 301);
    }

    // 3) 取 u.html,注入 handle + 語言 + 該使用者專屬 meta
    //    語言進網址(?hl=)才能被分語言收錄(Google 指引 + Strava/X 實務);無參數=預設繁中。
    const hlRaw = url.searchParams.get('hl');
    const hl = (hlRaw === 'en' || hlRaw === 'zh-hant' || hlRaw === 'zh-hans') ? hlRaw : null;
    const lang = hl || 'zh-hant';
    const page = await fetch(GH_ORIGIN + '/u.html');
    let html = await page.text();

    const display = prof && prof.is_public ? (prof.display_name || seg) : null;
    const canonBase = `${url.origin}/${seg}`;
    const canon = hl ? `${canonBase}?hl=${hl}` : canonBase;
    const title = display
      ? (lang === 'en' ? `${display}’s Musicals — MusicalMap`
        : lang === 'zh-hans' ? `${display} 的音乐剧足迹 — My Musicals | MusicalMap`
        : `${display} 的音樂劇足跡 — My Musicals | MusicalMap`)
      : (lang === 'en' ? 'This page doesn’t exist | MusicalMap'
        : lang === 'zh-hans' ? '找不到这个公开页 | MusicalMap'
        : '找不到這個公開頁 | MusicalMap');
    const desc = display
      ? (lang === 'en'
        ? `Musicals ${display} has seen around the world — poster wall, theatre passport and a map of every city. Build your own musical passport on MusicalMap.`
        : lang === 'zh-hans'
        ? `${display} 在世界各地看过的音乐剧——海报墙、音乐剧护照与足迹地图。用 MusicalMap 创建你自己的音乐剧护照。`
        : `${display} 在世界各地看過的音樂劇——海報牆、音樂劇護照與足跡地圖。用 MusicalMap 建立你自己的音樂劇護照。`)
      : (lang === 'en' ? 'It may have been removed, or the owner hasn’t made it public.'
        : lang === 'zh-hans' ? '这个收藏页不存在,或拥有者尚未公开。'
        : '這個收藏頁不存在,或擁有者尚未公開。');
    // hreflang:各語言版互列(zh-Hant=無參數版=x-default;en/zh-hans 各帶參數)
    const hreflang = display ? [
      `<link rel="alternate" hreflang="zh-Hant" href="${esc(canonBase)}" />`,
      `<link rel="alternate" hreflang="zh-Hans" href="${esc(canonBase)}?hl=zh-hans" />`,
      `<link rel="alternate" hreflang="en" href="${esc(canonBase)}?hl=en" />`,
      `<link rel="alternate" hreflang="x-default" href="${esc(canonBase)}" />`,
    ].join('\n') : '';
    const inject = [
      `<script>window.MM_HANDLE=${JSON.stringify(handle)};${hl ? `window.MM_HL=${JSON.stringify(hl)};` : ''}</script>`,
      `<link rel="canonical" href="${esc(canon)}" />`,
      hreflang,
      display ? '' : `<meta name="robots" content="noindex" />`,
      display ? `<script type="application/ld+json">${JSON.stringify({
        '@context': 'https://schema.org', '@type': 'ProfilePage',
        mainEntity: { '@type': 'Person', name: display, url: canonBase },
        about: 'Musical theatre viewing history', isPartOf: { '@type': 'WebSite', name: 'MusicalMap', url: MAIN_SITE },
      })}</script>` : '',
    ].filter(Boolean).join('\n');

    html = html
      .replace(/<html lang="[^"]*"/, `<html lang="${lang === 'en' ? 'en' : (lang === 'zh-hans' ? 'zh-Hans' : 'zh-Hant')}"`)
      .replace(/<title>[^<]*<\/title>/, `<title>${esc(title)}</title>\n<meta name="description" content="${esc(desc)}" />`)
      .replace(/(<meta property="og:title" content=")[^"]*(")/, `$1${esc(title)}$2`)
      .replace(/(<meta property="og:description" content=")[^"]*(")/, `$1${esc(desc)}$2`)
      .replace('</head>', `${inject}\n<meta property="og:url" content="${esc(canon)}" />\n</head>`);

    return new Response(html, {
      status: display ? 200 : 404,   // 查無 → 404(頁面本身會顯示 not-found 空狀態)
      headers: { 'content-type': 'text/html; charset=utf-8', 'cache-control': 'public, max-age=300' },
    });
  },
};
