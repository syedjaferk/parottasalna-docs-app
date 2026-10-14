// Header menus are <details> elements, so they open without JavaScript. This only closes them
// on a click outside, on Escape, and when another menu opens.
(function () {
  const menus = () => document.querySelectorAll("details.acct[open]");
  document.addEventListener("click", (e) => {
    menus().forEach((d) => { if (!d.contains(e.target)) d.open = false; });
  });
  document.addEventListener("keydown", (e) => {
    if (e.key !== "Escape") return;
    menus().forEach((d) => { d.open = false; d.querySelector("summary").focus(); });
  });
  document.addEventListener("toggle", (e) => {
    if (!e.target.matches || !e.target.matches("details.acct") || !e.target.open) return;
    menus().forEach((d) => { if (d !== e.target) d.open = false; });
  }, true);
})();
