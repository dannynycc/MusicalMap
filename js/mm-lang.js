/* Language switcher dropdown behaviour (shared by variant + legacy pages).
 * Markup: #lang-switch > button.lang-trigger[aria-expanded] + div.lang-pop[role=menu][hidden]
 * The <a> options keep their own href/data-hl-link — this only handles open/close + a11y.
 * No deps; safe to load defer on every page that renders #lang-switch. */
(function () {
  "use strict";
  function wire(root) {
    var trigger = root.querySelector(".lang-trigger");
    var pop = root.querySelector(".lang-pop");
    if (!trigger || !pop || trigger.dataset.wired) return;
    trigger.dataset.wired = "1";

    var open = function () {
      pop.hidden = false;
      trigger.setAttribute("aria-expanded", "true");
      document.addEventListener("click", onDocClick, true);
      document.addEventListener("keydown", onKey, true);
    };
    var close = function (focusBack) {
      pop.hidden = true;
      trigger.setAttribute("aria-expanded", "false");
      document.removeEventListener("click", onDocClick, true);
      document.removeEventListener("keydown", onKey, true);
      if (focusBack) trigger.focus();
    };
    var onDocClick = function (e) { if (!root.contains(e.target)) close(false); };
    var onKey = function (e) {
      var items = Array.prototype.slice.call(pop.querySelectorAll(".lang-opt"));
      var i = items.indexOf(document.activeElement);
      if (e.key === "Escape") { e.preventDefault(); close(true); }
      else if (e.key === "ArrowDown") { e.preventDefault(); (items[i + 1] || items[0]).focus(); }
      else if (e.key === "ArrowUp") { e.preventDefault(); (items[i - 1] || items[items.length - 1]).focus(); }
      else if (e.key === "Tab") { close(false); }  // let focus leave naturally
    };

    trigger.addEventListener("click", function (e) {
      e.preventDefault();
      if (pop.hidden) { open(); var cur = pop.querySelector(".lang-opt.active") || pop.querySelector(".lang-opt"); if (cur) cur.focus(); }
      else close(false);
    });
    // 選項點擊:變體頁(地圖 app)且 I18N.switchTo 存在 → 攔截,就地切語言(不重載,保留畫面);
    // 其餘(legacy 頁/無 app)→ 讓 <a> 照常導航。
    pop.addEventListener("click", function (e) {
      var a = e.target.closest && e.target.closest(".lang-opt");
      if (a && window.MM_VARIANT && window.I18N && typeof window.I18N.switchTo === "function") {
        var v = a.getAttribute("data-v");
        if (v) {
          e.preventDefault();
          window.I18N.switchTo(v);
          // 更新下拉內的 active 標示
          pop.querySelectorAll(".lang-opt").forEach(function (o) {
            var on = o.getAttribute("data-v") === v;
            o.classList.toggle("active", on);
            if (on) o.setAttribute("aria-current", "true"); else o.removeAttribute("aria-current");
          });
        }
      }
      close(false);
    });
  }
  function init() { document.querySelectorAll("#lang-switch").forEach(wire); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
  window.MM_WIRE_LANG = init;  // legacy pages can re-call after re-render
})();
