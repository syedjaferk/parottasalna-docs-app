/* Pattern guides: a short child-friendly summary per pattern, linking to the full lesson in the DSA Patterns course. */
(function () {
  const { esc, get } = window.Prep;
  const app = document.getElementById("patterns-app");
  const grid = document.getElementById("pattern-grid");
  let guides, cat;

  const slug = (s) => s.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");

  function card(name, n) {
    const g = guides[name], idx = cat.patterns.indexOf(name);
    const count = cat.problems.filter((p) => p.pa.includes(idx)).length;
    return `<article class="pattern-card card" id="${esc(slug(name))}">
      <header><span class="pnum">${String(n).padStart(2, "0")}</span><h2>${esc(name)}</h2></header>
      <p class="kid-line"><span aria-hidden="true">🧒</span> ${esc(g.kid)}</p>
      <h3>Spot it when…</h3>
      <ul>${g.when.map((x) => `<li>${esc(x)}</li>`).join("")}</ul>
      <p class="complexity"><span>Time <b>${esc(g.time)}</b></span><span>Space <b>${esc(g.space)}</b></span></p>
      <footer>
        <a class="btn sm" href="${esc(app.dataset.course + "sessions/" + g.session + ".html")}">Read the full lesson →</a>
        <a class="btn ghost sm" href="${esc(app.dataset.tracker)}#pattern=${esc(slug(name))}">Practise ${count} problems</a>
      </footer>
    </article>`;
  }

  function draw() {
    const q = document.getElementById("p-search").value.trim().toLowerCase();
    const names = Object.keys(guides).filter((n) => !q || n.toLowerCase().includes(q) || guides[n].kid.toLowerCase().includes(q));
    grid.innerHTML = names.map((n) => card(n, Object.keys(guides).indexOf(n) + 1)).join("") || '<p class="muted">No pattern matches.</p>';
  }

  Promise.all([get(app.dataset.guides), get(app.dataset.catalog)]).then(([g, c]) => { guides = g; cat = c; draw(); })
    .catch(() => { grid.innerHTML = '<p class="muted">Could not load the pattern guides.</p>'; });
  document.getElementById("p-search").addEventListener("input", window.Prep.debounce(draw, 120));
})();
