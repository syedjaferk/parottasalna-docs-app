/* Placement quiz: 21 "which technique fits?" questions, graded on the server. */
(function () {
  const { esc, get, post } = window.Prep;
  const app = document.getElementById("placement-app");
  const $ = (id) => document.getElementById(id);
  let questions = [];

  function render() {
    $("place-form").innerHTML = questions.map((q, i) => `<fieldset class="card q" data-id="${esc(q.id)}">
        <legend>Question ${i + 1} of ${questions.length}</legend>
        <p class="q-text">${esc(q.q)}</p>
        ${q.options.map((o, j) => `<label class="q-opt"><input type="radio" name="${esc(q.id)}" value="${j}"> <span>${esc(o)}</span></label>`).join("")}
        <label class="q-opt q-skip"><input type="radio" name="${esc(q.id)}" value="-1" checked> <span>I don't know yet</span></label>
      </fieldset>`).join("") + `<div class="place-submit"><button type="submit" class="btn">See my results</button></div>`;
  }

  $("place-start").onclick = async () => {
    $("place-start").disabled = true;
    try {
      questions = (await get(app.dataset.questions)).questions;
      render();
      $("place-intro").hidden = true;
      $("place-form").hidden = false;
      window.scrollTo(0, 0);
    } catch (e) { alert("Could not load the quiz. Please refresh."); $("place-start").disabled = false; }
  };

  $("place-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const answers = {};
    questions.forEach((q) => (answers[q.id] = +document.querySelector(`input[name="${q.id}"]:checked`).value));
    try {
      const res = await post(app.dataset.submit, { answers });
      show(res);
    } catch (err) { alert("Could not submit. Check your connection and try again."); }
  });

  const LEVEL_TEXT = {
    beginner: "You are at the start of the journey, and that is a great place to be. Your plan begins with the foundations and easy problems, with a short lesson for each new pattern.",
    intermediate: "You know a good number of patterns. Your plan starts with the ones that were new to you, and brings the ones you know up to medium difficulty.",
    advanced: "You recognise most patterns. Your plan leans towards medium and hard problems and the few patterns you missed.",
  };

  function show(res) {
    const byPattern = {};
    res.results.forEach((r) => ((byPattern[r.pattern] = byPattern[r.pattern] || []).push(r)));
    const known = Object.keys(byPattern).filter((p) => byPattern[p].filter((r) => r.correct).length / byPattern[p].length >= 0.5);
    const fresh = Object.keys(byPattern).filter((p) => !known.includes(p));
    const chips = (list, cls) => list.map((p) => `<span class="chip ${cls}">${esc(p)}</span>`).join(" ") || '<span class="muted">none</span>';
    const review = res.results.map((r, i) => {
      const q = questions[i];
      return `<details class="qa card ${r.correct ? "right" : "wrong"}"><summary><span>${r.correct ? "✅" : r.chosen === -1 ? "➖" : "❌"} ${esc(q.q)}</span></summary>
        <div class="ans"><p><strong>Best answer:</strong> ${esc(q.options[r.answer])}</p><p>${esc(r.why)}</p>
        <a href="${esc(app.dataset.course + "sessions/" + r.session + ".html")}">Read the ${esc(r.pattern)} lesson →</a></div></details>`;
    }).join("");
    $("place-form").hidden = true;
    const box = $("place-result");
    box.hidden = false;
    box.innerHTML = `<h2>Your level: <span class="lvl">${esc(res.level)}</span> <small class="muted">(${res.score} of ${res.total})</small></h2>
      <p>${esc(LEVEL_TEXT[res.level])}</p>
      <h3>You recognise</h3><p>${chips(known, "")}</p>
      <h3>New to you (we start here)</h3><p>${chips(fresh, "co")}</p>
      <div class="place-actions"><a class="btn" href="${esc(app.dataset.home)}">See my plan →</a></div>
      <h3>Review the answers</h3><div class="mat-body">${review}</div>`;
    window.scrollTo(0, 0);
  }
})();
