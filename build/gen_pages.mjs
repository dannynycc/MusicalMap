// gen_pages.mjs — 把 about/guide/privacy/terms 預先烘成三語靜態頁(同首頁的 / (en) /zh-hans/ /zh-hant/ 結構)。
// 動機:單一網址靠 client-side 換字,Googlebot 用英文環境渲染 → 中文搜尋出現英文標題+「翻譯這個網頁」。
// 來源模板在 build/pages/*.html(繁中為底+data-i18n 標記);字典取自 js/mm-strings.js(Node vm 執行,
// zh-hans 用 node_modules 的 opencc-js 重現瀏覽器端 CDN t2cn 的轉換+CN_FIX+HANS_OVERRIDE)。
// 產出:根 {slug}.html=英文版(en 住根,v2.54.0)+ {zh-hans,zh-hant}/{slug}.html;
//      /en/{slug} 由 _redirects 301 到根(舊連結不斷鏈)。路由頁已除役(root JS/302 分流讓
//      Google 把 root 判成 /en/ 重複的元凶,GSC 2026-07-19 實查)。
// 由 gen_site.mjs 匯入並呼叫;sitemap 的變體網址也在 gen_site.mjs 一併輸出。
// theatres.html 刻意不含:它是另一套 ?lang= 機制+內容全 JS 渲染,留待後續評估。
import fs from "node:fs";
import vm from "node:vm";
import { createRequire } from "node:module";

const SITE = "https://themusicalmap.com";
export const PAGE_SLUGS = ["about", "guide", "privacy", "terms"];
const LANGS = ["zh-hant", "zh-hans", "en"];
const HTML_LANG = { "zh-hant": "zh-Hant", "zh-hans": "zh-Hans", en: "en" };
const LANG_CODE = { "zh-hant": "繁中", "zh-hans": "简中", en: "EN" };
const TITLE_KEY = { about: "about_title", guide: "how_title", privacy: "pp_title", terms: "tou_title" };
const LPATH = (l) => (l === "en" ? "" : l + "/");   // en 住根(與 gen_site.mjs VPATH 同語意)

// ---- 字典:在 Node 裡執行 mm-strings.js(?hl=zh-hans 觸發簡中字典建置) ----
function loadDicts() {
  const require = createRequire(import.meta.url);
  const OpenCC = require("opencc-js");
  const src = fs.readFileSync("js/mm-strings.js", "utf8");
  const sandbox = {
    window: { OpenCC },
    document: { readyState: "loading", addEventListener() {}, querySelectorAll: () => [], documentElement: {} },
    location: { search: "?hl=zh-hans", href: `${SITE}/` },
    navigator: { language: "zh-TW" },
    URLSearchParams, URL,
  };
  vm.createContext(sandbox);
  vm.runInContext(src, sandbox);
  const STR = sandbox.window.MM_STR;
  if (!STR || !STR["zh-hans"]) throw new Error("gen_pages: zh-hans 字典未建成(opencc-js 載入失敗?)");
  return STR;
}

const esc = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
const escAttr = (s) => esc(s).replace(/"/g, "&quot;");

// dict 查值:變體缺 key 時退回繁中(與 runtime MM_T 同語意),並記錄缺口
function makeT(STR, lang, missing) {
  return (key) => {
    const d = STR[lang] || {};
    if (d[key] != null) return d[key];
    if (STR["zh-hant"][key] != null) { missing.push(`${lang}:${key}`); return STR["zh-hant"][key]; }
    throw new Error(`gen_pages: 字典完全沒有 key「${key}」`);
  };
}

// ---- 單頁轉換 ----
function bake(html, slug, lang, T) {
  let out = html;
  const url = `${SITE}/${LPATH(lang)}${slug}`;

  // 1) <html lang>
  out = out.replace(/<html lang="[^"]*">/, `<html lang="${HTML_LANG[lang]}">`);

  // 2) 語言釘選:放在 MM_USE_LANG_PREF 之後、OpenCC loader 之前。
  //    MM_HL 在 mm-strings 的判斷順序裡先於 localStorage/navigator → 靜態變體頁語言固定。
  const prefLine = "<script>window.MM_USE_LANG_PREF=true;</script>";
  if (!out.includes(prefLine)) throw new Error(`gen_pages: ${slug} 找不到 MM_USE_LANG_PREF 行`);
  out = out.replace(prefLine, `${prefLine}\n  <script>window.MM_HL="${lang}";window.MM_STATIC_VARIANT="${slug}";</script>`);

  // 3) OpenCC loader 的語言偵測補認 MM_HL(否則簡中變體頁不載 OpenCC,runtime 會把烘好的簡體蓋回繁體)
  const hook = "?h:null;";
  if (out.split(hook).length !== 2) throw new Error(`gen_pages: ${slug} loader hook 非唯一`);
  out = out.replace(hook, "?h:null;if(!v&&window.MM_HL)v=window.MM_HL;");

  // 4) 烘入翻譯 — 內文(data-i18n=textContent、data-i18n-html=innerHTML)
  out = out.replace(
    /(<([a-zA-Z][\w-]*)\b[^>]*?\bdata-i18n="([^"]+)"[^>]*>)([\s\S]*?)(<\/\2\s*>)/g,
    (_, open, _tag, key, _body, close) => open + esc(T(key)) + close
  );
  out = out.replace(
    /(<([a-zA-Z][\w-]*)\b[^>]*?\bdata-i18n-html="([^"]+)"[^>]*>)([\s\S]*?)(<\/\2\s*>)/g,
    (_, open, _tag, key, _body, close) => open + T(key) + close
  );
  // 屬性(meta content / placeholder / title / aria-label)
  const ATTR = [["data-i18n-content", "content"], ["data-i18n-ph", "placeholder"], ["data-i18n-title", "title"], ["data-i18n-aria", "aria-label"]];
  for (const [marker, attr] of ATTR) {
    // (?<![\w-]) 防止 content= 匹配到 data-i18n-content= 裡面(\b 在連字號後也成立)
    out = out.replace(new RegExp(`<[^>]*\\b${marker}="([^"]+)"[^>]*>`, "g"), (tag, key) =>
      tag.replace(new RegExp(`(?<![\\w-])${attr}="[^"]*"`), `${attr}="${escAttr(T(key))}"`)
    );
  }

  // 5) canonical / hreflang / og:url → 本變體
  out = out.replace(/<link rel="canonical" href="[^"]*" \/>/, `<link rel="canonical" href="${url}" />`);
  out = out.replace(/[ \t]*<link rel="alternate" hreflang="[^"]*" href="[^"]*" \/>\r?\n/g, "");
  out = out.replace(/(<link rel="canonical"[^>]*\/>\r?\n)/,
    `$1  <link rel="alternate" hreflang="en" href="${SITE}/${slug}" />\n` +
    `  <link rel="alternate" hreflang="zh-Hans" href="${SITE}/zh-hans/${slug}" />\n` +
    `  <link rel="alternate" hreflang="zh-Hant" href="${SITE}/zh-hant/${slug}" />\n` +
    `  <link rel="alternate" hreflang="x-default" href="${SITE}/${slug}" />\n`);
  out = out.replace(/<meta property="og:url" content="[^"]*"/, `<meta property="og:url" content="${url}"`);

  // 6) 相對資產 → 根絕對(變體頁在 /{lang}/ 底下,相對路徑會 404)
  out = out.replace(/((?:src|href)=")(css\/|js\/|assets\/|logo\.svg)/g, "$1/$2");
  // 6.5) guide 語言別截圖:直接烘入本語言版(JS 關閉的爬蟲也看到對的圖;runtime swap script 變 no-op)
  out = out.replace(/src="\/assets\/guide\/zh-hant\//g, `src="/assets/guide/${lang}/`);

  // 7) 站內連結 → 同語言變體(theatres 尚無變體,維持原樣)
  out = out.replace(/(<a\b[^>]*href=")\/(")/g, `$1/${LPATH(lang)}$2`);
  for (const s of PAGE_SLUGS) out = out.replace(new RegExp(`(<a\\b[^>]*href=")/${s}(")`, "g"), `$1/${LPATH(lang)}${s}$2`);

  // 8) 語言切換選單:?hl= → sibling 變體網址;目前語言標 aria-current
  out = out.replace(/(<a\b[^>]*data-hl-link="([^"]+)"[^>]*>)/g, (tag, _full, target) => {
    let t2 = tag.replace(/href="[^"]*"/, `href="/${LPATH(target)}${slug}"`);
    if (target === lang && !t2.includes("aria-current")) t2 = t2.replace(/>$/, ' aria-current="true">');
    return t2;
  });

  // 9) 語言切換觸發鈕短碼(runtime 也會設,烘入避免首繪錯字)
  out = out.replace(/(class="[^"]*lang-cur[^"]*"[^>]*>)[^<]*(<)/, `$1${LANG_CODE[lang]}$2`);

  return out;
}

export function genPages() {
  const STR = loadDicts();
  const missing = [];
  for (const slug of PAGE_SLUGS) {
    const src = fs.readFileSync(`build/pages/${slug}.html`, "utf8");
    for (const lang of LANGS) {
      const T = makeT(STR, lang, missing);
      const out = lang === "en" ? `${slug}.html` : `${lang}/${slug}.html`;   // en 住根(v2.54.0)
      if (lang !== "en") fs.mkdirSync(lang, { recursive: true });
      fs.writeFileSync(out, bake(src, slug, lang, T));
    }
  }
  const miss = [...new Set(missing)];
  console.log(`static pages: ${PAGE_SLUGS.length} slugs × ${LANGS.length} langs written (en at root)` +
    (miss.length ? `(缺譯退回繁中 ${miss.length}: ${miss.slice(0, 8).join(", ")}${miss.length > 8 ? "…" : ""})` : ""));
}
