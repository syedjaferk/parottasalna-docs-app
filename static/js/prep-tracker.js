/* Practice tracker: pick a sheet / company / pattern / topic, refine with filters, tick problems off. */
(function () {
  const { esc, get, post, safeUrl } = window.Prep;
  const app = document.getElementById("prep-app");
  const $ = (id) => document.getElementById(id);
  const DIFF_CLASS = ["basic", "easy", "medium", "hard"];
  const HEAT = { 1: "Cold", 2: "Warm", 3: "Hot", 4: "Very Hot" };
  const PAGE = 150;

  let cat, progress = {}, byId = {};
  const state = { mode: "sheet", item: null, shown: PAGE };
  const f = { q: "", diff: "", status: "", pattern: "", topic: "", company: "", heat: "" };

  /* ---- data ---------------------------------------------------------------------------- */
  const MODES = {
    sheet: () => cat.sheets.map((s) => ({ key: s.id, name: s.name, sub: s.by, ids: s.items.map((i) => i[0]) })),
    company: () => cat.companies.map((n, i) => ({ key: String(i), name: n, ids: idsWhere((p) => p.co.some((c) => c[0] === i)) })),
    pattern: () => cat.patterns.map((n, i) => ({ key: String(i), name: n, ids: idsWhere((p) => p.pa.includes(i)) })),
    topic: () => cat.topics.map((n, i) => ({ key: String(i), name: n, ids: idsWhere((p) => p.tg.includes(i)) })),
  };
  const groupsCache = {};
  const groups = (mode) => (groupsCache[mode] = groupsCache[mode] || MODES[mode]().filter((g) => g.ids.length));
  const idsWhere = (fn) => { const out = []; cat.problems.forEach((p, i) => fn(p) && out.push(i)); return out; };
  const done = (p) => !!(progress[p.id] && progress[p.id].s);

  /* ---- sidebar ------------------------------------------------------------------------- */
  function renderGroups() {
    const q = $("group-search").value.trim().toLowerCase();
    const list = groups(state.mode).filter((g) => !q || g.name.toLowerCase().includes(q));
    $("group-list").innerHTML = [`<li><button type="button" data-key="" class="${state.item === null ? "on" : ""}"><span>All problems</span><small>${cat.problems.filter(done).length}/${cat.problems.length}</small></button></li>`]
      .concat(list.map((g) => {
        const solved = g.ids.filter((i) => done(cat.problems[i])).length;
        return `<li><button type="button" data-key="${esc(g.key)}" class="${state.item === g.key ? "on" : ""}"><span>${esc(g.name)}${g.sub ? `<em>${esc(g.sub)}</em>` : ""}</span><small>${solved}/${g.ids.length}</small></button></li>`;
      })).join("");
  }

  /* ---- filtering ----------------------------------------------------------------------- */
  function currentRows() {
    // Each row: {i: index into cat.problems, section, sub}
    let rows;
    const g = state.item === null ? null : groups(state.mode).find((x) => x.key === state.item);
    if (state.mode === "sheet" && g) {
      const sheet = cat.sheets.find((s) => s.id === g.key);
      rows = sheet.items.map((it) => ({ i: it[0], section: it[1], sub: it[2] }));
    } else {
      const ids = g ? g.ids : cat.problems.map((_, i) => i);
      rows = ids.map((i) => ({ i }));
    }
    const q = f.q.trim().toLowerCase();
    const pat = f.pattern === "" ? null : +f.pattern, top = f.topic === "" ? null : +f.topic, com = f.company === "" ? null : +f.company;
    const heatFloor = f.heat ? +f.heat : 0;
    const companyForHeat = state.mode === "company" && g ? +g.key : com;
    return rows.filter(({ i }) => {
      const p = cat.problems[i], pr = progress[p.id] || {};
      if (q && !p.t.toLowerCase().includes(q)) return false;
      if (f.diff !== "" && p.d !== +f.diff) return false;
      if (pat !== null && !p.pa.includes(pat)) return false;
      if (top !== null && !p.tg.includes(top)) return false;
      if (com !== null && !p.co.some((c) => c[0] === com)) return false;
      if (heatFloor && companyForHeat !== null && !p.co.some((c) => c[0] === companyForHeat && c[1] >= heatFloor)) return false;
      if (f.status === "todo" && pr.s) return false;
      if (f.status === "done" && !pr.s) return false;
      if (f.status === "mark" && !pr.b) return false;
      if (f.status === "note" && !pr.n) return false;
      return true;
    });
  }

  /* ---- main list ----------------------------------------------------------------------- */
  function rowHtml({ i }) {
    const p = cat.problems[i], pr = progress[p.id] || {};
    const pats = p.pa.slice(0, 3).map((x) => `<button type="button" class="chip" data-pattern="${x}">${esc(cat.patterns[x])}</button>`).join("");
    const cos = p.co.slice().sort((a, b) => b[1] - a[1]).slice(0, 3).map((c) => `<button type="button" class="chip co h${c[1]}" data-company="${c[0]}" title="${HEAT[c[1]]}">${esc(cat.companies[c[0]])}</button>`).join("");
    const more = p.co.length > 3 ? `<span class="chip more" title="${p.co.slice(3).map((c) => esc(cat.companies[c[0]])).join(", ")}">+${p.co.length - 3}</span>` : "";
    return `<li class="prow${pr.s ? " solved" : ""}" data-id="${esc(p.id)}">
      <input type="checkbox" class="tick" aria-label="Mark ${esc(p.t)} as solved"${pr.s ? " checked" : ""}>
      <div class="pmain"><a class="ptitle" href="${esc(safeUrl(p.u))}" target="_blank" rel="noopener noreferrer">${esc(p.t)}</a>
        <div class="chips">${pats}${cos}${more}</div></div>
      <span class="plat">${esc(p.pl)}</span>
      <span class="diff ${DIFF_CLASS[p.d]}">${cat.difficulties[p.d]}</span>
      <button type="button" class="icon star${pr.b ? " on" : ""}" data-act="mark" aria-pressed="${!!pr.b}" aria-label="Bookmark" title="Bookmark">★</button>
      <button type="button" class="icon note${pr.n ? " on" : ""}" data-act="note" aria-label="Notes" title="${pr.n ? esc(pr.n.slice(0, 120)) : "Add a note"}">📝</button>
    </li>`;
  }

  function render() {
    const rows = currentRows();
    const all = viewRows();
    const solved = all.filter(({ i }) => done(cat.problems[i])).length;
    const g = state.item === null ? null : groups(state.mode).find((x) => x.key === state.item);
    $("view-title").textContent = g ? g.name : "All problems";
    $("view-sub").textContent = `${rows.length} shown${rows.length !== all.length ? ` of ${all.length}` : ""} · ${{ sheet: "Sheet", company: "Company", pattern: "Pattern", topic: "Topic" }[state.mode]}${g && g.sub ? " · by " + g.sub : ""}`;
    $("bar-fill").style.width = (all.length ? (solved / all.length) * 100 : 0) + "%";
    const byD = [0, 1, 2, 3].map((d) => {
      const tot = all.filter(({ i }) => cat.problems[i].d === d), s = tot.filter(({ i }) => done(cat.problems[i])).length;
      return tot.length ? `<span class="diff ${DIFF_CLASS[d]}">${cat.difficulties[d]} ${s}/${tot.length}</span>` : "";
    }).join(" ");
    $("bar-text").innerHTML = `<strong>${solved}</strong> / ${all.length} solved ${byD}`;
    $("f-heat-wrap").hidden = !(state.mode === "company" && g) && f.company === "";

    let html = "", n = 0, lastSec = null, lastSub = null;
    const slice = rows.slice(0, state.shown);
    for (const r of slice) {
      if (r.section !== undefined && (r.section !== lastSec || r.sub !== lastSub)) {
        if (lastSec !== null) html += "</ul>";
        const head = r.section + (r.sub && r.sub !== "General" && r.sub !== r.section ? " › " + r.sub : "");
        html += `<h3 class="sec">${esc(head)}</h3><ul class="plist">`;
        lastSec = r.section; lastSub = r.sub;
      } else if (n === 0) html += '<ul class="plist">';
      html += rowHtml(r); n++;
    }
    if (n) html += "</ul>";
    if (rows.length > slice.length) html += `<button type="button" class="btn ghost" id="show-more">Show ${Math.min(PAGE, rows.length - slice.length)} more (${rows.length - slice.length} left)</button>`;
    $("problems").innerHTML = n ? html : '<div class="card empty"><p class="muted">No problems match these filters.</p></div>';
    renderGroups();
  }

  // Rows of the selected group without the user filters (for the progress bar).
  function viewRows() {
    const saved = Object.assign({}, f);
    Object.keys(f).forEach((k) => (f[k] = ""));
    const rows = currentRows();
    Object.assign(f, saved);
    return rows;
  }

  /* ---- actions ------------------------------------------------------------------------- */
  const save = (id, patch) => {
    const cur = progress[id] || { s: false, b: false, n: "" };
    const next = Object.assign({}, cur, patch);
    if (!next.s && !next.b && !next.n) delete progress[id]; else progress[id] = next;
    const body = { id };
    if ("s" in patch) body.solved = patch.s;
    if ("b" in patch) body.bookmarked = patch.b;
    if ("n" in patch) body.note = patch.n;
    return post(app.dataset.set, body).catch(() => alert("Could not save. Check your connection and try again."));
  };

  $("problems").addEventListener("click", (e) => {
    const more = e.target.closest("#show-more");
    if (more) { state.shown += PAGE; render(); return; }
    const chip = e.target.closest(".chip[data-pattern],.chip[data-company]");
    if (chip) {
      if (chip.dataset.pattern) f.pattern = chip.dataset.pattern; else f.company = chip.dataset.company;
      syncFilters(); state.shown = PAGE; render(); return;
    }
    const li = e.target.closest(".prow");
    if (!li) return;
    const id = li.dataset.id, act = e.target.closest("[data-act]");
    if (e.target.classList.contains("tick")) {
      save(id, { s: e.target.checked }); li.classList.toggle("solved", e.target.checked); updateCounts();
    } else if (act && act.dataset.act === "mark") {
      const on = !(progress[id] && progress[id].b); save(id, { b: on });
      act.classList.toggle("on", on); act.setAttribute("aria-pressed", on);
    } else if (act && act.dataset.act === "note") openNote(id);
  });

  function updateCounts() { renderGroups(); const all = viewRows(); const s = all.filter(({ i }) => done(cat.problems[i])).length;
    $("bar-fill").style.width = (all.length ? (s / all.length) * 100 : 0) + "%"; render(); }

  // notes dialog
  let noteId = null;
  const dlg = $("note-dialog");
  function openNote(id) {
    noteId = id; $("note-title").textContent = "Notes · " + cat.problems[byId[id]].t;
    $("note-text").value = (progress[id] && progress[id].n) || ""; dlg.showModal(); $("note-text").focus();
  }
  $("note-cancel").onclick = () => dlg.close();
  $("note-save").onclick = () => { save(noteId, { n: $("note-text").value.trim() }).then(render); dlg.close(); };
  $("note-delete").onclick = () => { save(noteId, { n: "" }).then(render); dlg.close(); };

  // group + mode selection
  document.querySelector(".seg").addEventListener("click", (e) => {
    const b = e.target.closest("[data-mode]"); if (!b) return;
    state.mode = b.dataset.mode; state.item = null; state.shown = PAGE; $("group-search").value = ""; markMode(); writeHash(); render();
  });
  $("group-list").addEventListener("click", (e) => {
    const b = e.target.closest("button"); if (!b) return;
    state.item = b.dataset.key === "" ? null : b.dataset.key; state.shown = PAGE; writeHash(); render();
  });
  $("group-search").addEventListener("input", renderGroups);

  // filters
  function fill(sel, names, skip) { $(sel).insertAdjacentHTML("beforeend", names.map((n, i) => `<option value="${i}">${esc(n)}</option>`).join("")); }
  function syncFilters() { $("f-pattern").value = f.pattern; $("f-company").value = f.company; $("f-topic").value = f.topic; $("f-diff").value = f.diff; $("f-status").value = f.status; $("f-heat").value = f.heat; $("q").value = f.q; }
  [["f-diff", "diff"], ["f-status", "status"], ["f-pattern", "pattern"], ["f-topic", "topic"], ["f-company", "company"], ["f-heat", "heat"]].forEach(([id, key]) =>
    $(id).addEventListener("change", (e) => { f[key] = e.target.value; state.shown = PAGE; render(); }));
  $("q").addEventListener("input", window.Prep.debounce((e) => { f.q = e.target.value; state.shown = PAGE; render(); }, 150));
  $("btn-reset").onclick = () => { Object.keys(f).forEach((k) => (f[k] = "")); syncFilters(); state.shown = PAGE; render(); };

  // random unsolved problem from the current view
  $("btn-random").onclick = () => {
    const pool = currentRows().filter(({ i }) => !done(cat.problems[i]));
    if (!pool.length) return alert("Nothing unsolved left in this view. Nice work!");
    const pick = cat.problems[pool[Math.floor(Math.random() * pool.length)].i];
    window.open(safeUrl(pick.u), "_blank", "noopener,noreferrer");
  };

  // data menu
  $("btn-export").onclick = () => {
    const blob = new Blob([JSON.stringify({ version: 1, exported: new Date().toISOString(), progress }, null, 1)], { type: "application/json" });
    const a = document.createElement("a"); a.href = URL.createObjectURL(blob); a.download = "interview-prep-progress.json"; a.click(); URL.revokeObjectURL(a.href);
  };
  $("file-import").addEventListener("change", async (e) => {
    const file = e.target.files[0]; if (!file) return;
    try {
      const data = JSON.parse(await file.text());
      const res = await post(app.dataset.import, { progress: data.progress || {} });
      progress = res.progress; render(); alert(`Imported ${res.imported} problems.`);
    } catch (err) { alert("That file doesn't look like an exported progress file."); }
    e.target.value = "";
  });
  document.querySelectorAll("[data-clear]").forEach((b) => b.addEventListener("click", async () => {
    const all = b.dataset.all === "1";
    if (!confirm(all ? "Reset ALL your solved marks, bookmarks and notes?" : "Clear this for the problems in the current view?")) return;
    const ids = all ? undefined : viewRows().map(({ i }) => cat.problems[i].id);
    const res = await post(app.dataset.clear, { what: b.dataset.clear, ids });
    progress = res.progress; b.closest("details").open = false; render();
  }));

  /* ---- url hash ------------------------------------------------------------------------ */
  function writeHash() { history.replaceState(null, "", "#" + state.mode + (state.item !== null ? "=" + encodeURIComponent(state.item) : "")); }
  function readHash() {
    const m = decodeURIComponent(location.hash.slice(1)).match(/^(sheet|company|pattern|topic)(?:=(.*))?$/);
    if (m) { state.mode = m[1]; state.item = m[2] !== undefined && m[2] !== "" ? m[2] : null; }
    if (state.item !== null && !groups(state.mode).some((g) => g.key === state.item)) state.item = null;
  }
  function markMode() { document.querySelectorAll(".seg [data-mode]").forEach((b) => { const on = b.dataset.mode === state.mode; b.classList.toggle("on", on); b.setAttribute("aria-selected", on); }); }

  /* ---- boot ---------------------------------------------------------------------------- */
  Promise.all([get(app.dataset.catalog), get(app.dataset.progress)]).then(([c, p]) => {
    cat = c; progress = p.progress; cat.problems.forEach((x, i) => (byId[x.id] = i));
    fill("f-pattern", cat.patterns); fill("f-topic", cat.topics); fill("f-company", cat.companies);
    $("f-diff").insertAdjacentHTML("beforeend", cat.difficulties.map((n, i) => `<option value="${i}">${n}</option>`).join(""));
    readHash(); markMode(); render();
  }).catch(() => { $("view-title").textContent = "Could not load the problem catalog."; });
})();
