/* Pattern guides: a kid-friendly explanation plus the technical flow for every pattern, with practice problems. */
(function () {
  const { esc, get, safeUrl } = window.Prep;
  const app = document.getElementById("patterns-app");
  const grid = document.getElementById("pattern-grid");
  const DIFF = ["Basic", "Easy", "Medium", "Hard"];
  let guides, cat;

  function card(name) {
    const g = guides[name], idx = cat.patterns.indexOf(name);
    const probs = cat.problems.filter((p) => p.pa.includes(idx));
    const picks = probs.slice().sort((a, b) => a.d - b.d).filter((p) => p.pl === "leetcode").slice(0, 6);
    const list = (a) => a.map((x) => `<li>${esc(x)}</li>`).join("");
    return `<details class="pattern card" id="${esc(name.replace(/\W+/g, "-").toLowerCase())}" data-name="${esc(name.toLowerCase())}">
      <summary><h2>${esc(name)}</h2><span class="muted">${probs.length} problems · ${esc(g.time)}</span></summary>
      <div class="pbody">
        <div class="kid"><h3>🧒 Explained like you're 5</h3><p>${esc(g.kid)}</p></div>
        <div><h3>👀 Spot it when…</h3><ul>${list(g.when)}</ul></div>
        <div><h3>⚙️ The technical flow</h3><ol class="flow">${list(g.flow)}</ol></div>
        <div><h3>🧪 Template</h3><pre><code>${esc(g.code)}</code></pre>
          <p class="complexity"><span>Time <b>${esc(g.time)}</b></span><span>Space <b>${esc(g.space)}</b></span></p></div>
        <div><h3>⚠️ Common mistakes</h3><ul>${list(g.pitfalls)}</ul></div>
        <div><h3>🎯 Practise</h3><ul class="practice">${picks.map((p) => `<li><a href="${esc(safeUrl(p.u))}" target="_blank" rel="noopener noreferrer">${esc(p.t)}</a> <span class="diff ${DIFF[p.d].toLowerCase()}">${DIFF[p.d]}</span></li>`).join("")}</ul>
          <a class="btn ghost sm" href="${esc(app.dataset.tracker)}#pattern=${idx}">Open all ${probs.length} in the tracker →</a></div>
      </div></details>`;
  }

  function draw() {
    const q = document.getElementById("p-search").value.trim().toLowerCase();
    grid.innerHTML = cat.patterns.filter((n) => guides[n] && (!q || n.toLowerCase().includes(q))).map(card).join("") || '<p class="muted">No pattern matches.</p>';
    if (location.hash) { const el = document.getElementById(location.hash.slice(1)); if (el) { el.open = true; el.scrollIntoView(); } }
  }

  Promise.all([get(app.dataset.guides), get(app.dataset.catalog)]).then(([g, c]) => { guides = g; cat = c; draw(); })
    .catch(() => { grid.innerHTML = '<p class="muted">Could not load the pattern guides.</p>'; });
  document.getElementById("p-search").addEventListener("input", window.Prep.debounce(draw, 120));
})();
