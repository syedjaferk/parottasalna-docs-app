// Playground index: topic filter chips and per-problem progress bars.
// Signed-in visitors get the count from the server (data-done); anonymous ones from this browser's localStorage.
(function () {
  var grid = document.getElementById('sd-grid');
  if (!grid) return;
  var cards = Array.prototype.slice.call(grid.querySelectorAll('.sd-problem'));

  cards.forEach(function (card) {
    var total = Number(card.dataset.steps) || 1, done = 0;
    if (card.dataset.done !== undefined) done = Number(card.dataset.done) || 0;
    else {
      try {
        var raw = JSON.parse(localStorage.getItem('sd:' + card.dataset.slug) || 'null');
        if (raw && raw.answers) done = Object.keys(raw.answers).length;
      } catch (e) { /* storage blocked: show no progress */ }
    }
    if (!done) return;
    card.querySelector('.sd-prog span').style.width = Math.min(100, Math.round(100 * done / total)) + '%';
    card.querySelector('.sd-status').textContent = done >= total ? ' · completed ✓' : ' · ' + done + ' of ' + total + ' done';
  });

  var filters = document.getElementById('sd-filters');
  if (!filters) return;
  filters.addEventListener('click', function (e) {
    var btn = e.target.closest('.sd-chip');
    if (!btn) return;
    Array.prototype.forEach.call(filters.querySelectorAll('.sd-chip'), function (b) { b.setAttribute('aria-pressed', b === btn ? 'true' : 'false'); });
    cards.forEach(function (c) { c.hidden = !!btn.dataset.cat && c.dataset.cat !== btn.dataset.cat; });
  });
})();
