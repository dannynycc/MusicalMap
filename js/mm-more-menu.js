/* ≡ 選單開關(手機:使用指南 + 法務連結;桌面隱藏,見 css .more-menu)。
 * Markup: #more-menu > button.more-trigger[aria-expanded] + div.more-pop[role=menu][hidden]
 * 只處理 open/close + a11y;連結各自帶 href。無相依,defer 安全。
 * 仿 js/mm-lang.js。 */
(function () {
  "use strict";
  function wire(root) {
    var trigger = root.querySelector(".more-trigger");
    var pop = root.querySelector(".more-pop");
    if (!trigger || !pop || trigger.dataset.wired) return;
    trigger.dataset.wired = "1";

    function open() {
      pop.hidden = false;
      trigger.setAttribute("aria-expanded", "true");
      document.addEventListener("click", onDocClick, true);
      document.addEventListener("keydown", onKey, true);
    }
    function close(focusBack) {
      pop.hidden = true;
      trigger.setAttribute("aria-expanded", "false");
      document.removeEventListener("click", onDocClick, true);
      document.removeEventListener("keydown", onKey, true);
      if (focusBack) trigger.focus();
    }
    function onDocClick(e) { if (!root.contains(e.target)) close(false); }
    function onKey(e) {
      var items = Array.prototype.slice.call(pop.querySelectorAll(".more-opt"));
      var i = items.indexOf(document.activeElement);
      if (e.key === "Escape") { e.preventDefault(); close(true); }
      else if (e.key === "ArrowDown") { e.preventDefault(); (items[i + 1] || items[0]).focus(); }
      else if (e.key === "ArrowUp") { e.preventDefault(); (items[i - 1] || items[items.length - 1]).focus(); }
      else if (e.key === "Tab") { close(false); }
    }

    trigger.addEventListener("click", function (e) {
      e.preventDefault();
      if (pop.hidden) { open(); var first = pop.querySelector(".more-opt"); if (first) first.focus(); }
      else close(false);
    });
  }

  function init() {
    var root = document.getElementById("more-menu");
    if (root) wire(root);
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
