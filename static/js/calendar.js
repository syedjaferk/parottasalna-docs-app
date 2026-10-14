// Profile page "Add to your calendar": copy the feed link, and keep the daily reminder links in step
// with the chosen time and length. The links already work without this script (with the defaults).
(function () {
  document.querySelectorAll("[data-copy]").forEach((btn) => {
    btn.addEventListener("click", async () => {
      try {
        await navigator.clipboard.writeText(btn.dataset.copy);
        const old = btn.textContent;
        btn.textContent = "Copied ✓";
        setTimeout(() => { btn.textContent = old; }, 1800);
      } catch (e) {
        window.prompt("Copy this link:", btn.dataset.copy);
      }
    });
  });

  const box = document.querySelector("[data-reminder]");
  if (!box) return;
  const at = box.querySelector("[data-reminder-at]");
  const mins = box.querySelector("[data-reminder-mins]");
  const google = box.querySelector("[data-reminder-google]");
  const icsLink = box.querySelector("[data-reminder-ics]");
  const pad = (n) => String(n).padStart(2, "0");
  const stamp = (d) => `${d.getFullYear()}${pad(d.getMonth() + 1)}${pad(d.getDate())}T${pad(d.getHours())}${pad(d.getMinutes())}00`;

  function update() {
    const [h, m] = (at.value || "21:00").split(":").map(Number);
    const minutes = Number(mins.value);
    // The date is only the first occurrence; India time, so compare against "now" in IST.
    const nowIst = new Date(Date.now() + (330 + new Date().getTimezoneOffset()) * 60000);
    const start = new Date(nowIst.getFullYear(), nowIst.getMonth(), nowIst.getDate(), h, m);
    if (start <= nowIst) start.setDate(start.getDate() + 1);
    const end = new Date(start.getTime() + minutes * 60000);
    const url = new URL(google.href);
    url.searchParams.set("dates", `${stamp(start)}/${stamp(end)}`);
    const details = url.searchParams.get("details") || "";
    url.searchParams.set("details", details.replace(/^\d+ minutes/, `${minutes} minutes`));
    google.href = url.toString();
    icsLink.href = `${icsLink.pathname}?at=${pad(h)}:${pad(m)}&mins=${minutes}`;
  }
  at.addEventListener("change", update);
  mins.addEventListener("change", update);
})();
