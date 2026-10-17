/* The "log an attempt" dialog, shared by the Today page and the practice tracker.
   Prep.openLog({id, title, review, note, onSaved(entry)}) */
(function () {
  const dlg = document.getElementById("log-dialog");
  if (!dlg) return;
  const $ = (id) => document.getElementById(id);
  let ctx = null;

  const NEXT = {
    cold: "Great. You'll re-solve this from scratch in 1 day, then 1 week, then 3-4 weeks.",
    hint: "It goes back to the start of the queue: try it again from memory tomorrow.",
    fail: "No problem. It goes back in the queue for tomorrow. Read the approach, then try it again.",
  };
  const outcome = () => dlg.querySelector('input[name="outcome"]:checked').value;
  const confidence = () => +dlg.querySelector('input[name="confidence"]:checked').value;

  function hint() {
    const o = outcome(), low = o === "cold" && confidence() <= 2;
    $("log-next").textContent = low ? "A low confidence puts it back in tomorrow's queue even though you solved it." : NEXT[o];
  }
  dlg.addEventListener("change", hint);

  window.Prep.openLog = function (opts) {
    ctx = opts;
    $("log-title").textContent = (opts.review ? "Re-solve: " : "Log attempt: ") + opts.title;
    $("log-review").hidden = !opts.review;
    $("log-oldnote").hidden = !(opts.review && opts.note);
    $("log-oldnote-text").textContent = opts.note || "";
    $("log-minutes").value = "";
    $("log-note").value = opts.review ? opts.note || "" : opts.note || "";
    dlg.querySelector('input[name="outcome"][value="cold"]').checked = true;
    dlg.querySelector('input[name="confidence"][value="3"]').checked = true;
    hint();
    dlg.showModal();
    $("log-note").focus();
  };

  $("log-cancel").onclick = () => dlg.close();
  $("log-save").onclick = async () => {
    const body = { id: ctx.id, outcome: outcome(), note: $("log-note").value.trim() };
    if (outcome() !== "fail") body.confidence = confidence();
    const mins = parseInt($("log-minutes").value, 10);
    if (!isNaN(mins)) body.minutes = mins;
    $("log-save").disabled = true;
    try {
      const res = await window.Prep.post(dlg.dataset.url, body);
      dlg.close();
      if (ctx.onSaved) ctx.onSaved(res.entry);
    } catch (e) {
      alert("Could not save. Check your connection and try again.");
    } finally {
      $("log-save").disabled = false;
    }
  };
})();
