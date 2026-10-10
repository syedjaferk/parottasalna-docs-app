// Reading streak inside the Sphinx docs: counts active reading time and shows the 🔥 chip.
// "Active" = tab visible and the reader scrolled, typed, clicked or moved in the last 2 minutes.
// Time is sent every minute of reading, and whatever is left is sent when the reader leaves the page.
// Only for enrolled students (streak.json answers {"enabled": false} for everyone else).
(function () {
  var meta = document.querySelector('meta[name="portal-streak"]');
  var url = meta && meta.content;
  if (!url) return;

  var TICK = 5, IDLE_MS = 120000, PING_EVERY = 60, MIN_FLUSH = 5;
  var state = null, active = 0, lastInput = Date.now(), busy = false;

  function el(tag, cls, text) {
    var node = document.createElement(tag);
    if (cls) node.className = cls;
    if (text) node.textContent = text;
    return node;
  }
  function csrf() {
    var match = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/);
    return match ? decodeURIComponent(match[1]) : "";
  }
  function days(n) { return n + " day" + (n === 1 ? "" : "s"); }

  // ---------------------------------------------------------------- sidebar chip
  function renderChip() {
    var chip = document.querySelector(".streak-chip");
    if (!chip) {
      var anchor = document.querySelector(".sidebar-progress") || document.querySelector(".globaltoc");
      if (!anchor) return;
      chip = el("a", "streak-chip");
      chip.href = "/";
      chip.title = "Your reading streak (see the calendar on your dashboard)";
      anchor.insertAdjacentElement("beforebegin", chip);
    }
    chip.classList.toggle("is-done", state.today_done);
    chip.textContent = "";
    chip.appendChild(el("strong", null, "🔥 " + days(state.current) + " streak"));
    var hint;
    if (state.today_done) hint = "Done for today ✓";
    else if (state.status === "freeze") hint = "Read 1 min today — a freeze covers yesterday";
    else if (state.current > 0) hint = "Read 1 min today to keep it";
    else hint = "Read 1 min to start a streak";
    chip.appendChild(el("span", null, hint));
  }

  // ---------------------------------------------------------------- toast
  function toast(res) {
    var box = el("div", "streak-toast");
    box.setAttribute("role", "status");
    box.appendChild(el("strong", null, res.milestone
      ? "🏅 " + res.milestone + "-day streak! Milestone unlocked"
      : "🔥 Day " + res.current + " — streak extended!"));
    box.appendChild(el("span", null, res.next_milestone
      ? (res.next_milestone - res.current) + " more day" + (res.next_milestone - res.current === 1 ? "" : "s") + " to the " + res.next_milestone + "-day badge."
      : "See you tomorrow!"));
    document.body.appendChild(box);
    setTimeout(function () { box.classList.add("is-hiding"); }, 4500);
    setTimeout(function () { box.remove(); }, 5200);
  }

  // ---------------------------------------------------------------- active-time tracking
  ["scroll", "keydown", "mousemove", "mousedown", "touchstart", "wheel"].forEach(function (name) {
    window.addEventListener(name, function () { lastInput = Date.now(); }, { passive: true });
  });

  function ping() {
    var seconds = Math.min(active, 330);
    if (!seconds || busy) return;
    busy = true;
    active -= seconds;  // taken now, so a flush on leaving can't send the same seconds twice
    fetch(state.ping_url, {
      method: "POST", credentials: "same-origin",
      body: new URLSearchParams({ course: state.course, seconds: String(seconds) }),
      headers: { "X-CSRFToken": csrf(), "Accept": "application/json" }
    })
      .then(function (r) { if (!r.ok) throw r.status; return r.json(); })
      .then(function (res) {
        state.today_seconds = res.today_seconds;
        state.current = res.current; state.today_done = res.today_done; state.status = res.today_done ? "done" : state.status;
        renderChip();
        if (res.extended) toast(res);
      })
      .catch(function () { active += seconds; /* try again on the next tick */ })
      .then(function () { busy = false; });
  }

  function tick() {
    if (document.visibilityState === "visible" && Date.now() - lastInput < IDLE_MS) active += TICK;
    // Before today's goal, ping as soon as the goal is reached (so the toast shows on time).
    var threshold = state.today_done ? PING_EVERY : Math.max(Math.min(state.goal_seconds - state.today_seconds, PING_EVERY), TICK);
    if (active >= threshold) ping();
  }

  // Leaving the page, switching tabs or closing the window: send what's left. sendBeacon can't set
  // headers, so the CSRF token goes in the form body (Django accepts csrfmiddlewaretoken there).
  function flush() {
    var seconds = Math.min(active, 330);
    if (!state || seconds < MIN_FLUSH || !navigator.sendBeacon) return;
    var body = new URLSearchParams({ course: state.course, seconds: String(seconds), csrfmiddlewaretoken: csrf() });
    if (navigator.sendBeacon(state.ping_url, body)) {
      active -= seconds;
      state.today_seconds += seconds;
    }
  }
  document.addEventListener("visibilitychange", function () { if (document.visibilityState === "hidden") flush(); });
  window.addEventListener("pagehide", flush);

  fetch(url, { credentials: "same-origin", headers: { Accept: "application/json" } })
    .then(function (r) { return r.ok ? r.json() : null; })
    .then(function (data) {
      if (!data || !data.enabled) return;  // not enrolled: no streak, nothing stored
      state = data;
      renderChip();
      setInterval(tick, TICK * 1000);
    })
    .catch(function () {});
})();
