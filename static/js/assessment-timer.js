// The exam page: countdown, autosave, question palette and automatic submit when time is up.
// The server is the real clock; this script only shows it. See assessments/services.py.
(function () {
  var root = document.getElementById("exam");
  if (!root) return;
  var form = document.getElementById("exam-form");
  var timerEl = document.getElementById("timer");
  var trackEl = document.getElementById("track");
  var statusEl = document.getElementById("save-status");
  var announce = document.getElementById("announce");
  var overlay = document.getElementById("overlay");
  var progress = document.getElementById("answered");
  var questions = Array.prototype.slice.call(form.querySelectorAll(".as-q"));
  var dots = Array.prototype.slice.call(document.querySelectorAll(".as-dot"));

  var deadline = Number(root.dataset.deadline);
  var offset = Number(root.dataset.serverNow) - Date.now();     // server clock minus this computer's clock
  var total = Number(root.dataset.total) * 1000;
  var saveUrl = root.dataset.saveUrl;
  var csrf = form.querySelector("[name=csrfmiddlewaretoken]").value;
  var submitting = false, dirty = false, saveTimer = null, warned = {};

  function remainingMs() { return Math.max(0, deadline - (Date.now() + offset)); }
  function pad(n) { return (n < 10 ? "0" : "") + n; }

  function collect() {
    var data = {};
    questions.forEach(function (q) {
      var id = q.dataset.qid;
      data[id] = Array.prototype.slice.call(q.querySelectorAll("input:checked")).map(function (i) { return Number(i.value); });
    });
    return data;
  }

  function refreshAnswered() {
    var done = 0;
    questions.forEach(function (q, i) {
      var answered = !!q.querySelector("input:checked");
      if (answered) done++;
      if (dots[i]) dots[i].classList.toggle("done", answered);
    });
    progress.textContent = done + " of " + questions.length + " answered";
    return done;
  }

  function say(text) { announce.textContent = text; }

  function tick() {
    var ms = remainingMs(), s = Math.ceil(ms / 1000);
    var h = Math.floor(s / 3600), m = Math.floor((s % 3600) / 60), sec = s % 60;
    timerEl.textContent = (h ? h + ":" + pad(m) : m) + ":" + pad(sec);
    var totalSec = total / 1000;
    var level = s <= Math.min(60, totalSec * 0.1) ? "critical" : (s <= Math.min(300, totalSec * 0.25) ? "low" : "");
    timerEl.className = "as-timer " + level;
    trackEl.className = level;
    trackEl.style.width = Math.max(0, Math.min(100, ms / total * 100)) + "%";
    if (totalSec > 600 && s <= 300 && s > 60 && !warned.five) { warned.five = true; say("5 minutes left."); }
    if (totalSec > 120 && s <= 60 && s > 0 && !warned.one) { warned.one = true; say("1 minute left."); }
    if (ms <= 0) timeUp();
  }

  function save(keepalive) {
    dirty = false;
    statusEl.textContent = "Saving…";
    return fetch(saveUrl, {
      method: "POST", credentials: "same-origin", keepalive: !!keepalive,
      headers: { "Content-Type": "application/json", "X-CSRFToken": csrf },
      body: JSON.stringify({ answers: collect() })
    }).then(function (r) { return r.json(); }).then(function (data) {
      if (data.expired && !submitting) { timeUp(); return; }
      statusEl.textContent = "All answers saved ✓";
    }).catch(function () {
      dirty = true;
      statusEl.textContent = "Not saved: check your connection (retrying)";
    });
  }

  function scheduleSave() {
    dirty = true;
    statusEl.textContent = "Unsaved changes…";
    clearTimeout(saveTimer);
    saveTimer = setTimeout(save, 700);
  }

  function submit(auto) {
    if (submitting) return;
    submitting = true;
    window.removeEventListener("beforeunload", guard);
    if (auto) {
      overlay.hidden = false;
      var flag = document.createElement("input");
      flag.type = "hidden"; flag.name = "auto"; flag.value = "1";
      form.appendChild(flag);
    }
    form.submit();
  }
  function timeUp() { submit(true); }

  function guard(e) { if (!submitting) { e.preventDefault(); e.returnValue = ""; } }

  form.addEventListener("change", function () { refreshAnswered(); scheduleSave(); });
  form.addEventListener("submit", function (e) {
    if (submitting) return;
    var done = refreshAnswered();
    var left = questions.length - done;
    var msg = left ? left + " question(s) are unanswered. Submit anyway?" : "Submit your answers now? You cannot change them afterwards.";
    if (!window.confirm(msg)) { e.preventDefault(); return; }
    submitting = true;
    window.removeEventListener("beforeunload", guard);
  });
  dots.forEach(function (dot, i) {
    dot.addEventListener("click", function () { questions[i].scrollIntoView({ behavior: "smooth", block: "start" }); });
  });
  window.addEventListener("beforeunload", guard);
  document.addEventListener("visibilitychange", function () { if (document.visibilityState === "hidden" && dirty) save(true); });

  refreshAnswered();
  statusEl.textContent = "Answers are saved automatically";
  tick();
  setInterval(tick, 250);
  setInterval(function () { if (dirty) save(); }, 15000);
})();
