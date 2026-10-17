// Filters the catalogue cards as you type, and hides groups with no match.
(function () {
  var box = document.getElementById('cat-filter');
  if (!box) return;
  box.addEventListener('input', function () {
    var q = box.value.trim().toLowerCase();
    document.querySelectorAll('.cat-card').forEach(function (card) {
      card.hidden = q !== '' && card.dataset.search.indexOf(q) === -1;
    });
    document.querySelectorAll('.cat-group').forEach(function (group) {
      group.hidden = !group.querySelector('.cat-card:not([hidden])');
    });
  });
})();
