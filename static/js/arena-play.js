/* Live quiz: the player's phone screen. Talks to /ws/arena/<pin>/play/ (see arena/consumers.py).
   Everything shown from the server (questions, nicknames) goes through textContent, never innerHTML. */
(function () {
  "use strict";
  var root = document.getElementById("arena-play");
  if (!root) return;
  var pin = root.dataset.pin;
  var banner = document.querySelector("[data-banner]");
  var scoreEl = document.querySelector("[data-me-score]");
  var SHAPES = ["▲", "◆", "●", "■"];

  var socket = null, retry = 0, lastState = null, you = null, timer = null, myChoice = null, finished = false;

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

  // ---------------------------------------------------------------- socket
  function connect() {
    var proto = location.protocol === "https:" ? "wss://" : "ws://";
    socket = new WebSocket(proto + location.host + "/ws/arena/" + pin + "/play/");
    socket.onopen = function () { retry = 0; flash(""); };
    socket.onmessage = function (e) {
      var msg; try { msg = JSON.parse(e.data); } catch (_) { return; }
      if (msg.type === "state") { you = msg.you; render(msg.state); }
      else if (msg.type === "answered") { myChoice = msg.choice; renderAnswered(); }
      else if (msg.type === "error") { flash(msg.message); setTimeout(function () { flash(""); }, 3000); if (lastState) render(lastState); }
    };
    socket.onclose = function (e) {
      if (finished) return;
      if (e.code === 4403) { location.href = "/join/" + pin; return; }  // not a player (or the game is gone)
      flash("Reconnecting…");
      retry = Math.min(retry + 1, 6);
      setTimeout(connect, Math.min(1000 * Math.pow(2, retry - 1), 15000) + Math.random() * 500);
    };
  }
  function send(obj) { if (socket && socket.readyState === 1) socket.send(JSON.stringify(obj)); }

  // ---------------------------------------------------------------- screens
  function render(state) {
    var prev = lastState;
    lastState = state;
    if (you) scoreEl.textContent = you.score;
    if (!prev || prev.index !== state.index) myChoice = null;
    stopTimer();
    switch (state.status) {
      case "lobby": return renderLobby(state);
      case "question": return (you && you.answered) ? renderAnswered() : renderQuestion(state);
      case "reveal": return renderReveal(state);
      case "leaderboard": return renderBoard(state);
      case "finished": return renderFinished(state);
    }
  }

  function renderLobby(state) {
    show(el("p", "arena-big", "You're in! 🎉"),
         el("p", "arena-sub", "See your nickname on the big screen?"),
         el("p", "arena-rank", you ? you.nickname : ""),
         el("p", "arena-waiting", "Waiting for the host to start “" + state.title + "”…"));
  }

  function renderQuestion(state) {
    var q = state.question;
    var bar = el("div", "arena-timer"), fill = el("span");
    bar.appendChild(fill);
    var count = el("div", "arena-count");
    var tiles = el("div", "arena-tiles");
    q.choices.forEach(function (text, i) {
      var b = el("button", "arena-tile c" + i);
      b.type = "button";
      b.appendChild(el("span", "shape", SHAPES[i]));
      b.appendChild(el("span", "txt", text));
      b.setAttribute("aria-label", "Answer " + (i + 1) + ": " + text);
      b.addEventListener("click", function () {
        tiles.querySelectorAll("button").forEach(function (t) { t.disabled = true; if (t !== b) t.classList.add("dim"); });
        send({ action: "answer", choice: i });
      });
      tiles.appendChild(b);
    });
    show(el("p", "arena-progress", "Question " + (state.index + 1) + " of " + state.total),
         el("div", "arena-question", q.text), count, bar, tiles);
    countdown(q.remaining_ms, q.time_limit * 1000, count, fill, function () {
      tiles.querySelectorAll("button").forEach(function (t) { t.disabled = true; });
    });
  }

  function renderAnswered() {
    if (!lastState || lastState.status !== "question") return;
    stopTimer();
    var q = lastState.question, nodes = [el("p", "arena-big", "Answer locked in 🔒")];
    if (myChoice !== null && q.choices[myChoice] !== undefined) {
      var t = el("div", "arena-tile c" + myChoice);
      t.appendChild(el("span", "shape", SHAPES[myChoice]));
      t.appendChild(el("span", "txt", q.choices[myChoice]));
      nodes.push(el("div", "arena-tiles"));
      nodes[1].style.gridTemplateColumns = "1fr";
      nodes[1].appendChild(t);
    }
    nodes.push(el("p", "arena-waiting", "Waiting for everyone else…"));
    show.apply(null, nodes);
  }

  function renderReveal(state) {
    var last = you && you.last, box;
    if (!last) {
      box = el("div", "arena-result meh");
      box.append(el("div", "emoji", "⌛"), el("p", "arena-big", "No answer"), el("div", "points", "+0"));
    } else if (last.correct) {
      box = el("div", "arena-result good");
      box.append(el("div", "emoji", "✅"), el("p", "arena-big", "Correct!"), el("div", "points", "+" + last.points));
    } else {
      box = el("div", "arena-result bad");
      box.append(el("div", "emoji", "❌"), el("p", "arena-big", "Not this time"), el("div", "points", "+0"));
    }
    var right = (state.reveal ? state.reveal.correct : []).map(function (i) {
      return SHAPES[i] + " " + state.question.choices[i];
    }).join("  ·  ");
    show(box, el("p", "arena-sub", "Answer: " + right), rankLine());
  }

  function rankLine() {
    return el("p", "arena-rank", you ? "You're #" + you.rank + " with " + you.score + " pts" : "");
  }

  function boardList(rows) {
    var ol = el("ol", "arena-board");
    rows.forEach(function (r, i) {
      var li = el("li");
      if (you && r.nickname === you.nickname) li.classList.add("you");
      li.style.animationDelay = (i * 0.05) + "s";
      li.append(el("span", "pos", String(i + 1)), el("span", "name", r.nickname), el("span", "pts", String(r.score)));
      ol.appendChild(li);
    });
    return ol;
  }

  function renderBoard(state) {
    show(el("p", "arena-big", "Leaderboard"), boardList(state.leaderboard || []), rankLine(),
         el("p", "arena-waiting", "Next question coming up…"));
  }

  function renderFinished(state) {
    finished = true;
    var medal = you && you.rank <= 3 ? ["🥇", "🥈", "🥉"][you.rank - 1] : "🎉";
    show(el("div", "arena-result meh"), el("p", "arena-big", "Thanks for playing!"),
         boardList(state.leaderboard || []));
    var box = root.firstChild;
    box.append(el("div", "emoji", medal), el("p", "arena-big", you ? "#" + you.rank : ""),
               el("div", "points", (you ? you.score : 0) + " pts"));
    if (socket) socket.close();
  }

  // ---------------------------------------------------------------- countdown
  function countdown(remainingMs, totalMs, countEl, fillEl, onEnd) {
    var end = Date.now() + remainingMs;
    function tick() {
      var left = Math.max(0, end - Date.now());
      countEl.textContent = Math.ceil(left / 1000);
      fillEl.style.width = (totalMs ? (left / totalMs) * 100 : 0) + "%";
      if (left <= 0) { stopTimer(); onEnd(); }
    }
    tick();
    timer = setInterval(tick, 100);
  }

  connect();
})();
