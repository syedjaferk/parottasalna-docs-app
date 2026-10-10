// Keeps the "Today's live sessions" card current without a reload: countdown, "Live now",
// "Ended", and turns the Join button on 15 minutes before the start.
(function () {
  var card = document.querySelector("[data-live-card]");
  if (!card) return;

  function untilText(ms) {
    var mins = Math.max(1, Math.round(ms / 60000));
    if (mins < 60) return "Starts in " + mins + " min";
    var h = Math.floor(mins / 60), m = mins % 60;
    return "Starts in " + h + " h" + (m ? " " + m + " min" : "");
  }

  function update() {
    var now = Date.now();
    card.querySelectorAll(".live-item").forEach(function (item) {
      if (item.hasAttribute("data-cancelled")) return;
      var start = Date.parse(item.dataset.start), end = Date.parse(item.dataset.end);
      var joinFrom = Date.parse(item.dataset.joinFrom);
      var status = now >= end ? "ended" : now >= start ? "live" : now >= joinFrom ? "soon" : "upcoming";
      item.className = "live-item is-" + status;

      var badge = item.querySelector("[data-live-badge]");
      if (badge) {
        badge.textContent = status === "live" ? "🔴 Live now"
          : status === "soon" ? untilText(start - now)
          : status === "ended" ? "Ended" : untilText(start - now);
      }
      var join = item.querySelector("[data-live-join]");
      if (!join) return;
      if (status === "ended") { join.remove(); return; }
      var waiting = status === "upcoming";
      join.classList.toggle("is-waiting", waiting);
      if (waiting) { join.setAttribute("aria-disabled", "true"); join.setAttribute("tabindex", "-1"); }
      else { join.removeAttribute("aria-disabled"); join.removeAttribute("tabindex"); }
      var label = join.querySelector("[data-live-join-label]");
      if (label) label.textContent = waiting ? "Join opens 15 min before" : "Join on Google Meet";
    });
  }

  update();
  setInterval(update, 20000);
  document.addEventListener("visibilitychange", function () { if (!document.hidden) update(); });
})();
