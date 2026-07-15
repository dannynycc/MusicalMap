/* 跨網域語言傳遞(themusicalmap.com ↔ my.themusicalmap.com)
 * 問題:兩個網域的語言偏好各存各的 localStorage,互跳時對方用「自己上次」的語言
 * (使用者在 zh-hant 的 my. 頁點「地圖首頁」,主頁卻用它記得的 en)。
 * 解法:點擊前把跨網域連結改寫成帶語言——地圖首頁走語言路徑(/zh-hant/ 等),
 * 其他頁補 ?hl=;同網域連結不動(自家 localStorage 會記)。適用全站所有情境。 */
(function () {
  "use strict";
  function variant() {
    try {
      var q = new URLSearchParams(location.search).get("hl");
      if (q === "en" || q === "zh-hans" || q === "zh-hant") return q;
      if (window.MM_VARIANT) return window.MM_VARIANT;
      if (window.MM_HL) return window.MM_HL;
      var mv = localStorage.getItem("mm_variant");
      if (mv === "en" || mv === "zh-hans" || mv === "zh-hant") return mv;
      var ml = localStorage.getItem("mm_lang");
      if (ml === "en") return "en";
      if (ml === "zh") return "zh-hant";
    } catch (e) { /* private mode 等 */ }
    return null;
  }
  function rewrite() {
    var v = variant(); if (!v) return;
    var here = location.hostname;
    var as = document.querySelectorAll('a[href^="https://themusicalmap.com"],a[href^="https://my.themusicalmap.com"]');
    for (var i = 0; i < as.length; i++) {
      var a = as[i];
      try {
        var u = new URL(a.getAttribute("href"));
        if (u.hostname === here) continue;                    // 同網域:自家會記,不動
        if (a.hasAttribute("data-hl-link")) continue;         // 語言切換選單本身不動
        if (u.hostname === "themusicalmap.com" && (u.pathname === "/" || u.pathname === "")) {
          u.pathname = v === "zh-hans" ? "/zh-hans/" : v === "en" ? "/en/" : "/zh-hant/";
        } else if (/^\/(zh-hant|zh-hans|en)(\/|$)/.test(u.pathname)) {
          /* 已是語言路徑(前次 rewrite 產物):不再補 ?hl,否則第二次點擊變 /zh-hant/?hl=zh-hant 冗餘雙標(2026-07-15 修) */
        } else if (!u.searchParams.get("hl")) {
          u.searchParams.set("hl", v);
        }
        a.setAttribute("href", u.toString());
      } catch (e) { /* 非法 URL 跳過 */ }
    }
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", rewrite);
  else rewrite();
  // 動態插入的連結(頭像選單/JS 組的 footer)+切換語言後再點:導航前(capture)再掃一次
  document.addEventListener("click", function (e) {
    if (e.target && e.target.closest && e.target.closest("a[href]")) rewrite();
  }, true);
})();
