/* Live quiz: the host's big screen. Talks to /ws/arena/<pin>/host/ (see arena/consumers.py).
   Nicknames and questions are rendered with textContent only. */
(function () {
  "use strict";
  var root = document.getElementById("arena-host");
  if (!root) return;
  var pin = root.dataset.pin;
  var banner = document.querySelector("[data-banner]");
  var playersEl = document.querySelector("[data-players]");
  var SHAPES = ["▲", "◆", "●", "■"];

  var socket = null, retry = 0, state = null, nicknames = [], timer = null, finished = false;
  var answeredEl = null, chipsEl = null;

  function el(tag, cls, text) {
    var node = document.createElement(tag);
    if (cls) node.className = cls;
    if (text !== undefined && text !== null) node.textContent = text;
    return node;
  }
  function show() { root.replaceChildren.apply(root, arguments); }
  function flash(msg) {
    if (!msg) { banner.hidden = true; return; }
    banner.textContent = msg; banner.hidden = false;
  }
  function stopTimer() { if (timer) { clearInterval(timer); timer = null; } }
  function button(label, action, cls) {
    var b = el("button", "arena-btn " + (cls || "big"), label);
    b.type = "button";
    b.addEventListener("click", function () {
      if (action === "finish" && !confirm("End the game for everyone now?")) return;
      b.disabled = true;
      send({ action: action });
    });
    return b;
  }

  // ---------------------------------------------------------------- socket
  function connect() {
    var proto = location.protocol === "https:" ? "wss://" : "ws://";
    socket = new WebSocket(proto + location.host + "/ws/arena/" + pin + "/host/");
    socket.onopen = function () { retry = 0; flash(""); };
    socket.onmessage = function (e) {
      var msg; try { msg = JSON.parse(e.data); } catch (_) { return; }
      if (msg.type === "state") {
        if (msg.extras) nicknames = msg.extras.nicknames || [];
        render(msg.state);
      } else if (msg.type === "counts") {
        nicknames = msg.nicknames || nicknames;
        playersEl.textContent = msg.players;
        if (state) { state.players = msg.players; state.answered = msg.answered; }
        updateLive();
      } else if (msg.type === "error") {
        flash(msg.message);
        setTimeout(function () { flash(""); }, 3000);
        if (state) render(state);
      }
    };
    socket.onclose = function (e) {
      if (finished) return;
      if (e.code === 4403) { flash("This game is over or you can't host it."); return; }
      flash("Reconnecting…");
      retry = Math.min(retry + 1, 6);
      setTimeout(connect, Math.min(1000 * Math.pow(2, retry - 1), 15000));
    };
  }
  function send(obj) { if (socket && socket.readyState === 1) socket.send(JSON.stringify(obj)); }

  // ---------------------------------------------------------------- screens
  function render(s) {
    state = s;
    playersEl.textContent = s.players;
    answeredEl = chipsEl = null;
    stopTimer();
    switch (s.status) {
      case "lobby": return renderLobby(s);
      case "question": return renderQuestion(s);
      case "reveal": return renderReveal(s);
      case "leaderboard": return renderBoard(s);
      case "finished": return renderFinished(s);
    }
  }

  // Counts arrive between full states (someone joined / answered): patch in place.
  function updateLive() {
    if (!state) return;
    if (chipsEl) fillChips();
    if (answeredEl) answeredEl.textContent = state.answered + " / " + state.players + " answered";
  }
  function fillChips() {
    chipsEl.replaceChildren.apply(chipsEl, nicknames.map(function (n) { return el("span", null, n); }));
    if (!nicknames.length) chipsEl.appendChild(el("p", "arena-waiting", "Waiting for players…"));
  }

  function renderLobby(s) {
    var pinBox = el("div", "arena-pin-box");
    pinBox.append(el("div", "lbl", "Go to " + root.dataset.join.replace(/^https?:\/\//, "") + " and enter"),
                  el("div", "pin", s.pin));
    chipsEl = el("div", "arena-chips");
    fillChips();
    var controls = el("div", "arena-controls");
    controls.append(button("Start ▶", "start"));
    show(el("p", "arena-big", s.title), pinBox, chipsEl, controls);
  }

  function tiles(s, reveal) {
    var wrap = el("div", "arena-tiles");
    s.question.choices.forEach(function (text, i) {
      var t = el("div", "arena-tile c" + i);
      t.append(el("span", "shape", SHAPES[i]), el("span", "txt", text));
      if (reveal) {
        if (reveal.correct.indexOf(i) >= 0) { t.classList.add("right"); t.appendChild(el("span", "tick", "✓")); }
        else t.classList.add("dim");
      }
      wrap.appendChild(t);
    });
    return wrap;
  }

  function renderQuestion(s) {
    var q = s.question;
    var count = el("div", "arena-count"), bar = el("div", "arena-timer"), fill = el("span");
    bar.appendChild(fill);
    answeredEl = el("p", "arena-sub");
    updateLive();
    var controls = el("div", "arena-controls");
    controls.append(button("Reveal now", "reveal", "ghost"));
    show(el("p", "arena-progress", "Question " + (s.index + 1) + " of " + s.total), el("div", "arena-question", q.text),
         count, bar, answeredEl, tiles(s), controls);
    var end = Date.now() + q.remaining_ms, total = q.time_limit * 1000;
    function tick() {
      var left = Math.max(0, end - Date.now());
      count.textContent = Math.ceil(left / 1000);
      fill.style.width = (left / total) * 100 + "%";
      if (left <= 0) stopTimer();  // the server reveals on its own timer
    }
    tick();
    timer = setInterval(tick, 100);
  }

  function renderReveal(s) {
    var counts = s.reveal.counts, max = Math.max.apply(null, counts.concat([1]));
    var bars = el("div", "arena-bars");
    bars.style.setProperty("--n", counts.length);
    counts.forEach(function (n, i) {
      var col = el("div", "arena-bar-col c" + i + (s.reveal.correct.indexOf(i) >= 0 ? "" : " wrong"));
      var fill = el("div", "fill");
      fill.style.height = "0%";
      col.append(el("div", "label", n), fill, el("div", "label", SHAPES[i]));
      bars.appendChild(col);
      requestAnimationFrame(function () { requestAnimationFrame(function () { fill.style.height = (n / max) * 80 + "%"; }); });
    });
    var last = s.index + 1 >= s.total;
    var controls = el("div", "arena-controls");
    controls.append(button("Leaderboard", "leaderboard"));
    controls.append(button(last ? "Final results 🏆" : "Next question ▶", "next", "ghost"));
    show(el("div", "arena-question", s.question.text), bars, tiles(s, s.reveal),
         el("p", "arena-sub", s.answered + " of " + s.players + " answered"), controls);
  }

  function boardList(rows) {
    var ol = el("ol", "arena-board");
    rows.forEach(function (r, i) {
      var li = el("li");
      li.style.animationDelay = (i * 0.06) + "s";
      li.append(el("span", "pos", String(i + 1)), el("span", "name", r.nickname), el("span", "pts", String(r.score)));
      ol.appendChild(li);
    });
    return ol;
  }

  function renderBoard(s) {
    var last = s.index + 1 >= s.total;
    var controls = el("div", "arena-controls");
    controls.append(button(last ? "Final results 🏆" : "Next question ▶", "next"));
    show(el("p", "arena-big", "Leaderboard"), boardList(s.leaderboard || []), controls);
  }

  function renderFinished(s) {
    finished = true;
    var rows = s.leaderboard || [], podium = el("div", "arena-podium");
    ["🥇", "🥈", "🥉"].forEach(function (medal, i) {
      if (!rows[i]) return;
      var step = el("div", "step p" + (i + 1));
      step.append(el("span", "medal", medal), el("span", "who", rows[i].nickname), el("span", "pts", rows[i].score + " pts"));
      podium.appendChild(step);
    });
    var controls = el("div", "arena-controls");
    var csv = el("a", "arena-btn big", "Download results (CSV)"); csv.href = root.dataset.results;
    var home = el("a", "arena-btn ghost", "Back to quizzes"); home.href = root.dataset.home;
    controls.append(csv, home);
    show(el("p", "arena-big", "🏆 " + s.title), rows.length ? podium : el("p", "arena-sub", "Nobody played."),
         boardList(rows.slice(3)), controls);
    if (socket) socket.close();
  }

  connect();
})();
