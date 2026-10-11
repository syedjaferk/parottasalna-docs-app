/* Live classroom polls: keeps the result bars up to date over /ws/polls/<code>/ (read-only feed).
   Used by the teacher's present page and by students' vote page. All text goes in via textContent. */
(function () {
  "use strict";
  var root = document.querySelector("[data-poll-live]");
  if (!root) return;
  var code = root.dataset.code;
  var mode = root.dataset.mode;          // "present" or "vote"
  var retry = 0;

  document.querySelectorAll("[data-confirm]").forEach(function (btn) {
    btn.addEventListener("click", function (e) {
      if (!window.confirm(btn.dataset.confirm)) e.preventDefault();
    });
  });

  function connect() {
    var proto = location.protocol === "https:" ? "wss://" : "ws://";
    var ws = new WebSocket(proto + location.host + "/ws/polls/" + code + "/");
    ws.onopen = function () { retry = 0; };
    ws.onmessage = function (e) {
      var msg;
      try { msg = JSON.parse(e.data); } catch (_) { return; }
      if (msg.type === "state") render(msg.state);
    };
    ws.onclose = function (e) {
      if (e.code === 4404) return;        // poll deleted
      retry = Math.min(retry + 1, 6);
      setTimeout(connect, Math.min(1000 * Math.pow(2, retry - 1), 15000) + Math.random() * 500);
    };
  }

  function render(state) {
    if (mode === "vote") {
      // The teacher opened/closed voting or toggled results: re-render the page from the server.
      var wasOpen = root.dataset.open === "1", hadResults = root.dataset.results === "1";
      if (state.is_open !== wasOpen || state.show_results !== hadResults) {
        location.reload();
        return;
      }
    } else {
      var badge = root.querySelector("[data-status]");
      if (badge) {
        badge.textContent = state.is_open ? "● live" : "closed";
        badge.classList.toggle("is-open", state.is_open);
      }
    }
    if (!state.counts) return;             // results hidden from this viewer
    var total = state.total;
    root.querySelectorAll("[data-bars] [data-i]").forEach(function (li) {
      var i = Number(li.dataset.i), n = state.counts[i] || 0;
      var pct = total ? Math.round((100 * n) / total) : 0;
      var countEl = li.querySelector("[data-count]");
      if (Number(countEl.textContent) !== n) {
        countUp(countEl, n);
        li.classList.remove("bump");
        void li.offsetWidth;                // restart the flash animation
        li.classList.add("bump");
      }
      li.querySelector("[data-pct]").textContent = pct;
      li.querySelector("[data-fill]").style.width = pct + "%";
    });
    var totalEl = root.querySelector("[data-total]");
    if (totalEl) countUp(totalEl, total);
    var word = root.querySelector("[data-votes-word]");
    if (word) word.textContent = total === 1 ? "vote" : "votes";
  }

  function countUp(el, target) {
    var start = Number(el.textContent) || 0, t0 = null;
    if (start === target) return;
    if (document.hidden) {                 // animation frames don't run in background tabs
      el.textContent = target;
      return;
    }
    function step(ts) {
      if (t0 === null) t0 = ts;
      var k = Math.min(1, (ts - t0) / 400);
      el.textContent = Math.round(start + (target - start) * k);
      if (k < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }

  connect();
})();
