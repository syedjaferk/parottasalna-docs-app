/* Shared helpers for the interview-prep pages. */
(function () {
  const cookie = (n) => (document.cookie.match(new RegExp("(?:^|; )" + n + "=([^;]*)")) || [])[1] || "";
  window.Prep = {
    esc(s) {
      return String(s == null ? "" : s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
    },
    async get(url) {
      const r = await fetch(url, { credentials: "same-origin" });
      if (!r.ok) throw new Error(url + " " + r.status);
      return r.json();
    },
    async post(url, body) {
      const r = await fetch(url, {
        method: "POST", credentials: "same-origin",
        headers: { "Content-Type": "application/json", "X-CSRFToken": decodeURIComponent(cookie("csrftoken")) },
        body: JSON.stringify(body),
      });
      if (!r.ok) throw new Error(url + " " + r.status);
      return r.json();
    },
    safeUrl(u) { return /^https?:\/\//i.test(u || "") ? u : "#"; },
    debounce(fn, ms) { let t; return (...a) => { clearTimeout(t); t = setTimeout(() => fn(...a), ms); }; },
  };
})();
