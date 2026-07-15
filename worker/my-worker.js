/* Cloudflare Worker — my.themusicalmap.com/<handle> 個人公開頁
   (docs/DESIGN_username_sharing.md 網址層實作;部署步驟見 docs/SETUP_MY_SUBDOMAIN.md)

   做三件事:
   1. 乾淨網址:/<handle> 內部改寫成 GitHub Pages 的 u.html(注入 window.MM_HANDLE,前端照常跑)。
   2. 舊名 301:handle 查無 → resolve_handle(舊名→現用名)→ 301 到新網址(alias 永久有效)。
   3. 爬蟲可見:回傳前注入該使用者專屬 <title>/description/og/canonical/JSON-LD
      (u.html 原本純前端 render,爬蟲/AI 什麼都看不到;這層補上,對標 flightradar24 個人頁)。

   資安:此處只用公開 anon key + 只讀公開資料(profiles 的 RLS 只放行 is_public;
   resolve_handle 只回公開帳號)。無任何秘密,程式碼可公開。 */

const GH_ORIGIN = 'https://musicalmap.pages.dev';   // 素材來源=Cloudflare Pages(2026-07-06 託管遷移;同家調貨,CI 雙部署位元級同步)
const MAIN_SITE = 'https://themusicalmap.com';
const SUPABASE_URL = 'https://gtuvrhdvwjlvneispcuq.supabase.co';
const ANON_KEY = 'sb_publishable_liJcmr-g9eU9xLLkKixJaA_9s8YjCni';   // 公開 key(RLS 把關)

// 與 DB handle_reserved()、me.html RESERVED 同步(supabase/add_handle_aliases.sql)
const RESERVED = new Set(['u','me','index','admin','api','app','www','my','null','undefined',
  'theatres','privacy','terms','login','logout','signup','settings','account','stats','static',
  'assets','js','css','data','posters','logos','en','zh-hant','zh-hans','help','about','official','map','share','guide','me-input']);

const esc = (s) => String(s ?? '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
// JSON-LD 內嵌 <script> 安全序列化:JSON.stringify 不會轉義 '</script>'(也不轉 < & U+2028/2029),
// 使用者自訂 display_name 含 </script> 可提前關閉腳本標籤 → 儲存型 XSS。把 <>& 與行分隔符轉成 \uXXXX,
// JSON parser 仍能正確解回,但 HTML parser 不會把它看成標籤邊界。
const jsonLd = (obj) => JSON.stringify(obj)
  .replace(/</g,'\\u003c').replace(/>/g,'\\u003e').replace(/&/g,'\\u0026')
  .replace(/\u2028/g,'\\u2028').replace(/\u2029/g,'\\u2029');

// Web Analytics:不在此注入統計碼。2026-07-06 API 實證——手動 snippet 上報在本帳號從未入帳,
// 唯一有效機制=zone 的 RUM 自動注入(edge 對經過 Cloudflare 的 HTML 回應自動加 beacon,含本 Worker 的輸出,
// 早上 10:15-12:15 的 my./主站事件皆由它入帳)。手工再埋反而有雙重注入風險。統計設定=WA 站點選「Enable(自動注入)」。
const withBeacon = (html) => html;   // 保留掛點:若日後要 Worker 端注入,改這裡一處即可

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
    // 根 = 「我的音樂劇」入口,直接出內容不 302(FR24 模式:my. 就是個人應用的家;
    // 登入後前端 replaceState 把網址列改成 /<handle>,不重載)。app shell 登入閘,不快取。
    if (path === '/' || path === '') {
      const shell = await fetch(GH_ORIGIN + '/me.html');
      return new Response(withBeacon(await shell.text()), {
        headers: { 'content-type': 'text/html; charset=utf-8', 'cache-control': 'private, no-store' },
      });
    }

    const seg = path.replace(/^\/+|\/+$/g, '');
    // 含 . 或 / 的是靜態資源(css/js/data/posters/圖檔) → 代理 GitHub Pages。
    // cache-control 壓回 10 分鐘:Cloudflare 會把瀏覽器 TTL 拉到預設 4 小時,
    // 造成部署後 my. 網域使用者拿舊 JS/CSS 最多 4 小時;與主站(GH Pages 600s)對齊。
    if (seg.includes('.') || seg.includes('/')) {
      const r = await fetch(GH_ORIGIN + path + url.search);
      const h = new Headers(r.headers);
      h.set('cache-control', 'public, max-age=600');
      // .html 頁(如 iframe 的 me-input.html)也注入統計碼;其他資源原樣串流
      if (/\.html$/.test(path)) {
        return new Response(withBeacon(await r.text()), { status: r.status, headers: h });
      }
      return new Response(r.body, { status: r.status, headers: h });
    }
    // 保留字不是 handle → settings 留在本 origin(session 住 my.,設定頁必須同源才讀得到登入);其餘丟回主站
    if (seg.toLowerCase() === 'settings') return Response.redirect(url.origin + '/settings.html' + url.search, 302);
    if (RESERVED.has(seg.toLowerCase())) return Response.redirect(MAIN_SITE, 302);

    // 尾斜線正規化(相對路徑解析需要 /danny 而非 /danny/)
    if (path.endsWith('/')) return Response.redirect(url.origin + '/' + seg, 301);

    const handle = seg.toLowerCase();

    // 0) FR24 式同網址:本人(mm_owner cookie 相符)→ 同網址出「編輯版」me.html。
    //    cookie 只是選版面的提示,偽造只會拿到登入閘;資料權限由 Supabase session+RLS 把關。
    //    private no-store:編輯版絕不可被快取共用。
    const ck = req.headers.get('Cookie') || '';
    const own = ck.match(/(?:^|;\s*)mm_owner=([A-Za-z0-9_%-]+)/);
    if (own && decodeURIComponent(own[1]).toLowerCase() === handle) {
      const owner = await fetch(GH_ORIGIN + '/me.html');
      return new Response(withBeacon(await owner.text()), {
        status: 200,
        headers: { 'content-type': 'text/html; charset=utf-8', 'cache-control': 'private, no-store' },
      });
    }

    // 1) 查現用 handle(RLS:只回公開帳號 → 私密帳號自然走 not-found,不洩漏存在性)
    const profs = await sbGet(`/rest/v1/profiles?select=display_name,is_public&handle=eq.${encodeURIComponent(handle)}&limit=1`);
    const prof = profs && profs[0];

    // 2) 查無 → 舊名?301 到現用名(alias 永久有效)
    if (!prof || !prof.is_public) {
      const nh = await sbRpc('resolve_handle', { p_handle: handle });
      if (nh && nh !== handle) return Response.redirect(url.origin + '/' + encodeURIComponent(nh), 301);   // 與前端 u-view 一致編碼(handle 格式驗證下目前無實害,防禦一致性;2026-07-15)
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
      display ? `<script type="application/ld+json">${jsonLd({
        '@context': 'https://schema.org', '@type': 'ProfilePage',
        mainEntity: { '@type': 'Person', name: display, url: canonBase },
        about: 'Musical theatre viewing history', isPartOf: { '@type': 'WebSite', name: 'MusicalMap', url: MAIN_SITE },
      })}</script>` : '',
    ].filter(Boolean).join('\n');

    // 可見 H1:靜態 u.html 是寫死「My Musicals」,每個 profile 都一樣→爬蟲看到重複 H1、
    // 無法為「<名字> musicals」收錄(SEO 2026-07-10)。有效公開頁改寫成擁有者專屬 H1。
    const h1txt = display
      ? (lang === 'en' ? `${display}’s Musicals`
        : lang === 'zh-hans' ? `${display} 的音乐剧收藏`
        : `${display} 的音樂劇收藏`)
      : null;

    // 全部用「函式型替換」:第二參數是 function 時,回傳字串中的 $&/$1/$` 等序列不會被當回填指令。
    // esc(display_name) 可能含 $2、$& 之類序列(display_name 是使用者自訂),字串型替換會把它們展開成
    // 匹配片段 → 破壞 meta 標籤/屬性。函式型徹底規避。
    html = html
      .replace(/<html lang="[^"]*"/, `<html lang="${lang === 'en' ? 'en' : (lang === 'zh-hans' ? 'zh-Hans' : 'zh-Hant')}"`)
      .replace(/<title>[^<]*<\/title>/, () => `<title>${esc(title)}</title>\n<meta name="description" content="${esc(desc)}" />`)
      .replace(/(<meta property="og:title" content=")[^"]*(")/, (m, p1, p2) => `${p1}${esc(title)}${p2}`)
      .replace(/(<meta property="og:description" content=")[^"]*(")/, (m, p1, p2) => `${p1}${esc(desc)}${p2}`)
      .replace('</head>', () => `${inject}\n<meta property="og:url" content="${esc(canon)}" />\n</head>`);
    if (h1txt) html = html.replace('<h1>My Musicals</h1>', () => `<h1>${esc(h1txt)}</h1>`);

    return new Response(withBeacon(html), {
      status: display ? 200 : 404,   // 查無 → 404(頁面本身會顯示 not-found 空狀態)
      // Vary: Cookie:同網址依 mm_owner 出不同版面,瀏覽器快取必須跟著 cookie 區分,
      // 否則本人登入後可能拿到快取的公開版(反之亦然)。
      headers: { 'content-type': 'text/html; charset=utf-8', 'cache-control': 'public, max-age=300', 'vary': 'Cookie' },
    });
  },
};
