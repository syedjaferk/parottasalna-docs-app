// Answers the "code smell of the day" quiz (templates/smells/_daily.html).
(function () {
  var card = document.querySelector('[data-smell]');
  if (!card) return;
  var buttons = Array.prototype.slice.call(card.querySelectorAll('.smell-choice'));
  var result = card.querySelector('[data-result]');
  var busy = false;

  function show(data) {
    buttons.forEach(function (b, i) {
      b.disabled = true;
      if (i === data.answer) b.classList.add('is-correct');
      else if (i === data.your_choice) b.classList.add('is-wrong');
    });
    result.textContent = '';
    var head = document.createElement('strong');
    head.textContent = data.correct ? '✅ Correct!' : '❌ Not quite.';
    result.appendChild(head);
    if (data.explanation) result.appendChild(document.createTextNode(data.explanation));
    result.hidden = false;
  }

  function submit(i) {
    if (busy) return;
    busy = true;
    var body = new URLSearchParams({ slug: card.dataset.slug, choice: i });
    fetch(card.dataset.answerUrl, {
      method: 'POST', credentials: 'same-origin', body: body,
      headers: { 'X-CSRFToken': card.dataset.csrf },
    }).then(function (r) { return r.ok ? r.json() : Promise.reject(r); })
      .then(show)
      .catch(function () { result.textContent = 'Could not check your answer. Try again.'; result.hidden = false; busy = false; });
  }

  buttons.forEach(function (b) { b.addEventListener('click', function () { submit(Number(b.dataset.i)); }); });
  // Already answered today: re-show the result (the server returns the stored answer).
  if (card.dataset.prevChoice !== undefined) submit(Number(card.dataset.prevChoice));
})();
