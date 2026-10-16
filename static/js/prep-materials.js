/* Study material: HR / SQL / CS question banks, role-wise questions, system design, notes, playlists, cold emails, resumes. */
(function () {
  const { esc, get, safeUrl } = window.Prep;
  const app = document.getElementById("materials-app");
  const $ = (id) => document.getElementById(id);
  const PAGE = 40;
  const base = app.dataset.base.replace(/mat_hr\.json$/, "");
  const SETS = [
    { key: "hr", label: "HR questions", kind: "qa" }, { key: "sql", label: "SQL practice", kind: "qa" },
    { key: "cs", label: "Core CS questions", kind: "qa", group: true }, { key: "roles", label: "Role-wise questions", kind: "qa", group: true },
    { key: "system_design", label: "System design", kind: "sd" }, { key: "playlists", label: "Video playlists", kind: "pl" },
    { key: "notes", label: "Notes & PDFs", kind: "notes" }, { key: "cold_emails", label: "Cold email templates", kind: "mail" },
    { key: "resumes", label: "Resume templates", kind: "res" },
  ];
  const cache = {};
  let cur = SETS[0], items = [], shown = PAGE;
  const label = (s) => s.replace(/-/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());

  $("mat-list").innerHTML = SETS.map((s) => `<li><button type="button" data-key="${s.key}"><span>${s.label}</span></button></li>`).join("");

  async function open(set) {
    cur = set; shown = PAGE;
    document.querySelectorAll("#mat-list button").forEach((b) => b.classList.toggle("on", b.dataset.key === set.key));
    $("m-q").value = ""; $("m-title").innerHTML = `<h2>${set.label}</h2>`; $("m-body").innerHTML = '<p class="muted">Loading…</p>';
    if (!cache[set.key]) cache[set.key] = await get(`${base}mat_${set.key}.json`);
    items = cache[set.key];
    const cats = [...new Set(items.map((x) => set.group && x.s ? x.s : x.c || x.cat || x.category).filter(Boolean))].sort();
    $("m-cat").innerHTML = '<option value="">All</option>' + cats.map((c) => `<option value="${esc(c)}">${esc(label(c))}</option>`).join("");
    $("m-cat-wrap").hidden = cats.length < 2;
    const diffs = [...new Set(items.map((x) => x.d).filter(Boolean))];
    $("m-diff").innerHTML = '<option value="">All</option>' + diffs.map((d) => `<option>${esc(d)}</option>`).join("");
    $("m-diff-wrap").hidden = diffs.length < 2;
    draw();
  }

  const text = (x) => Object.values(x).filter((v) => typeof v === "string").join(" ").toLowerCase();

  function filtered() {
    const q = $("m-q").value.trim().toLowerCase(), c = $("m-cat").value, d = $("m-diff").value;
    return items.filter((x) => (!q || text(x).includes(q)) && (!c || (cur.group && x.s ? x.s : x.c || x.cat || x.category) === c) && (!d || x.d === d));
  }

  const link = (u, t) => `<a href="${esc(safeUrl(u))}" target="_blank" rel="noopener noreferrer">${esc(t)}</a>`;
  const ITEM = {
    qa: (x) => `<details class="qa card"><summary><span>${esc(x.q)}</span>${x.d ? `<span class="diff ${esc(x.d.toLowerCase())}">${esc(x.d)}</span>` : ""}</summary><div class="ans">${x.c ? `<p class="muted">${esc(label(x.s || x.c))}${x.s ? " · " + esc(x.c) : ""}</p>` : ""}<pre class="ans-text">${esc(x.a)}</pre></div></details>`,
    sd: (x) => `<div class="card mat-row"><div><strong>${esc(x.t)}</strong> <span class="chip">${esc(x.type)}</span><div class="chips">${x.companies.map((c) => `<span class="chip">${esc(c)}</span>`).join("")}</div></div><div class="mat-links">${x.article ? link(x.article, "Article") : ""}${x.video ? link(x.video, "Video") : ""}</div></div>`,
    pl: (x) => `<div class="card mat-row"><div><strong>${link(x.u, x.t)}</strong><div class="muted">${esc(x.pl)} · ${esc(x.sec)}</div></div></div>`,
    notes: (x) => `<div class="card mat-row"><div><strong>${link(x.url, x.t)}</strong> <span class="chip">${esc(x.cat)}</span></div></div>`,
    mail: (x) => `<details class="qa card"><summary><span>${esc(x.title)}</span><span class="chip">${esc(x.category)}</span></summary><div class="ans"><p class="muted">${esc(x.purpose)}</p><p><b>Subject:</b> ${esc(x.subject)}</p><pre class="ans-text">${esc(x.body)}</pre>${x.tips ? `<p class="muted"><b>Tips:</b> ${esc(x.tips)}</p>` : ""}<button type="button" class="btn ghost sm" data-copy="${esc(x.subject + "\n\n" + x.body)}">Copy email</button></div></details>`,
    res: (x) => `<div class="card mat-row"><strong>${link(x.u, x.t)}</strong></div>`,
  };

  function draw() {
    const rows = filtered();
    $("m-title").innerHTML = `<h2>${cur.label}</h2><span class="count">${rows.length}</span>`;
    $("m-body").innerHTML = rows.slice(0, shown).map(ITEM[cur.kind]).join("") || '<p class="muted">Nothing matches.</p>';
    $("m-more").hidden = rows.length <= shown;
    $("m-more").textContent = `Show more (${rows.length - shown} left)`;
  }

  $("mat-list").addEventListener("click", (e) => { const b = e.target.closest("button"); if (b) open(SETS.find((s) => s.key === b.dataset.key)); });
  $("m-more").onclick = () => { shown += PAGE; draw(); };
  ["m-cat", "m-diff"].forEach((id) => $(id).addEventListener("change", () => { shown = PAGE; draw(); }));
  $("m-q").addEventListener("input", window.Prep.debounce(() => { shown = PAGE; draw(); }, 150));
  $("m-body").addEventListener("click", (e) => {
    const b = e.target.closest("[data-copy]");
    if (b && navigator.clipboard) navigator.clipboard.writeText(b.dataset.copy).then(() => { b.textContent = "Copied ✓"; });
  });
  open(SETS[0]);
})();
