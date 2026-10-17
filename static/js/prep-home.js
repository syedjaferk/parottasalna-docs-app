/* Today page: what to re-solve, what to try next, and how well each pattern is covered. */
(function () {
  const { esc, get, safeUrl } = window.Prep;
  const app = document.getElementById("home-app");
  const $ = (id) => document.getElementById(id);
  const DIFF = ["Basic", "Easy", "Medium", "Hard"];
  const slug = (s) => s.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
  let plan, guides = {};

  const lesson = (pattern) => (guides[pattern] ? `${app.dataset.course}sessions/${guides[pattern].session}.html` : null);
  const diff = (d) => `<span class="diff ${DIFF[d].toLowerCase()}">${DIFF[d]}</span>`;

  function banner() {
    const p = plan.placement;
    $("home-banner").innerHTML = p.taken
      ? `<div class="card banner ok"><div>🧭 Your level: <strong>${esc(p.level)}</strong> (${p.score}/${p.total} on the placement quiz). Your plan starts with the patterns that were new to you.</div><a class="btn ghost sm" href="${esc(app.dataset.placement)}">Retake</a></div>`
      : `<div class="card banner"><div><strong>New here? Take the 5-minute placement quiz.</strong><br><span class="muted">It finds which patterns you already know, so we can start you in the right place.</span></div><a class="btn" href="${esc(app.dataset.placement)}">Take the quiz →</a></div>`;
  }

  function stats() {
    const s = plan.stats;
    const cell = (n, label, cls = "") => `<div class="stat-box ${cls}"><strong>${n}</strong><span>${label}</span></div>`;
    $("home-stats").innerHTML = cell(s.due, "due to re-solve", s.due ? "hot" : "") + cell(s.upcoming, "due this week") + cell(s.solved, "solved") + cell(s.mastered, "mastered") +
      cell(s.week_solved, "new this week") + cell(s.week_reviews, "re-solves this week") + cell(s.streak + (s.streak === 1 ? " day" : " days"), "streak", s.streak ? "streak" : "");
  }

  function reviews() {
    $("rev-count").textContent = plan.reviews.length;
    if (!plan.reviews.length) {
      $("rev-list").innerHTML = `<p class="empty-line">Nothing due. ${plan.stats.upcoming ? `${plan.stats.upcoming} coming up in the next 7 days.` : "Solve a few new problems and they will show up here for re-solving."}</p>`;
      return;
    }
    $("rev-list").innerHTML = plan.reviews.slice(0, 12).map((r) => `<div class="todo" data-id="${esc(r.id)}">
        <div class="todo-main"><a href="${esc(safeUrl(r.url))}" target="_blank" rel="noopener noreferrer">${esc(r.title)}</a>
          <div class="chips">${diff(r.difficulty)}${r.patterns.slice(0, 2).map((p) => `<span class="chip">${esc(p)}</span>`).join("")}<span class="chip co">${esc(r.stage_label)}${r.overdue ? ` · ${r.overdue}d overdue` : ""}</span></div></div>
        <button type="button" class="btn sm" data-act="resolve">Re-solve</button></div>`).join("") +
      (plan.reviews.length > 12 ? `<p class="muted small">+${plan.reviews.length - 12} more. Finish these first.</p>` : "");
  }

  function next() {
    $("rotated").hidden = !plan.rotated.length;
    if (plan.rotated.length) $("rotated").innerHTML = `🔀 You have solved a lot of <strong>${plan.rotated.map(esc).join(", ")}</strong> in a row, so it is skipped for now. Mixing patterns makes them stick.`;
    if (!plan.next.length) { $("next-list").innerHTML = '<p class="empty-line">You have covered every pattern. Pick harder problems in the tracker.</p>'; return; }
    $("next-list").innerHTML = plan.next.map((n) => `<div class="todo" data-id="${esc(n.id)}">
        <div class="todo-main"><a href="${esc(safeUrl(n.url))}" target="_blank" rel="noopener noreferrer">${esc(n.title)}</a>
          <div class="chips">${diff(n.difficulty)}<span class="chip">${esc(n.pattern)}</span></div>
          <p class="why">${esc(n.why)}${lesson(n.pattern) ? ` <a href="${esc(lesson(n.pattern))}">Read the lesson</a>` : ""}</p></div>
        <button type="button" class="btn ghost sm" data-act="log">Log attempt</button></div>`).join("");
  }

  function coverage() {
    $("cov-grid").innerHTML = plan.patterns.map((p) => {
      const pct = Math.min(100, Math.round((p.solved / p.target) * 100));
      return `<a class="cov" href="${esc(app.dataset.tracker)}#pattern=${esc(slug(p.name))}">
        <div class="cov-top"><strong>${esc(p.name)}</strong>${p.familiar ? '<span class="tick-mark" title="Recognised in the placement quiz">✓</span>' : ""}</div>
        <div class="bar"><span style="width:${pct}%"></span></div>
        <div class="cov-meta"><span>${p.solved}/${p.target} solved</span>${p.due ? `<span class="chip co">${p.due} due</span>` : ""}${p.mastered ? `<span class="chip">${p.mastered} mastered</span>` : ""}</div></a>`;
    }).join("");
  }

  const titleOf = (id) => ((plan.reviews.concat(plan.next)).find((x) => x.id === id) || {}).title || id;
  const noteOf = (id) => ((plan.reviews.find((x) => x.id === id) || {}).note) || "";

  document.addEventListener("click", (e) => {
    const b = e.target.closest("[data-act]");
    if (!b) return;
    const row = b.closest(".todo");
    if (!row) return;
    const id = row.dataset.id;
    window.Prep.openLog({ id, title: titleOf(id), review: b.dataset.act === "resolve", note: noteOf(id), onSaved: load });
  });

  function draw() { banner(); stats(); reviews(); next(); coverage(); }
  function load() { return get(app.dataset.next).then((p) => { plan = p; draw(); }); }
  get(app.dataset.guides).then((g) => (guides = g)).catch(() => {}).then(load)
    .catch(() => { $("home-banner").innerHTML = '<div class="card">Could not load your plan. Please refresh.</div>'; });
})();
