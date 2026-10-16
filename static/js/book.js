// Story reader: reading-progress bar, current-section highlight in the contents list, copy buttons on code.
(function () {
  var body = document.getElementById("story-body");
  if (!body) return;

  var bar = document.getElementById("read-progress");
  function progress() {
    var max = document.documentElement.scrollHeight - window.innerHeight;
    bar.style.width = (max > 0 ? Math.min(100, (window.scrollY / max) * 100) : 0) + "%";
  }
  window.addEventListener("scroll", progress, { passive: true });
  progress();

  var links = {};
  document.querySelectorAll(".chapter-toc a[href^='#']").forEach(function (a) { links[a.getAttribute("href").slice(1)] = a; });
  if ("IntersectionObserver" in window) {
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting || !links[entry.target.id]) return;
        Object.keys(links).forEach(function (id) { links[id].classList.remove("on"); });
        links[entry.target.id].classList.add("on");
      });
    }, { rootMargin: "-10% 0px -80% 0px" });
    body.querySelectorAll("h2").forEach(function (h) { observer.observe(h); });
  }

  body.querySelectorAll("pre").forEach(function (pre) {
    var text = pre.innerText;
    var btn = document.createElement("button");
    btn.type = "button"; btn.className = "copy-btn"; btn.textContent = "Copy";
    btn.addEventListener("click", function () {
      navigator.clipboard.writeText(text).then(function () {
        btn.textContent = "Copied!"; setTimeout(function () { btn.textContent = "Copy"; }, 1500);
      });
    });
    pre.appendChild(btn);
  });
})();
