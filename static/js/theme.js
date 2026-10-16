// Light / dark / system theme. Loaded in <head> without defer so the saved choice is applied before
// first paint (no flash). "system" removes data-theme so the CSS follows the OS preference.
// The key matches the course notes (docs) pages, so one choice covers the whole site.
(function () {
  var KEY = "_theme";
  var root = document.documentElement;

  function saved() {
    try { var v = localStorage.getItem(KEY); return v === "light" || v === "dark" ? v : "system"; }
    catch (e) { return "system"; }
  }
  function apply(pref) {
    if (pref === "system") root.removeAttribute("data-theme"); else root.setAttribute("data-theme", pref);
    root.setAttribute("data-theme-pref", pref);
  }
  function mark(pref) {
    document.querySelectorAll("[data-theme-set]").forEach(function (b) {
      b.setAttribute("aria-pressed", String(b.getAttribute("data-theme-set") === pref));
    });
  }

  apply(saved());

  document.addEventListener("DOMContentLoaded", function () {
    mark(saved());
    document.addEventListener("click", function (e) {
      var b = e.target.closest && e.target.closest("[data-theme-set]");
      if (!b) return;
      var pref = b.getAttribute("data-theme-set");
      try { if (pref === "system") localStorage.removeItem(KEY); else localStorage.setItem(KEY, pref); } catch (err) {}
      apply(pref);
      mark(pref);
      var d = b.closest("details"); if (d) d.open = false;
    });
  });
  // Other tabs (or the docs pages) changed the choice.
  window.addEventListener("storage", function (e) { if (e.key === KEY) { apply(saved()); mark(saved()); } });
})();
