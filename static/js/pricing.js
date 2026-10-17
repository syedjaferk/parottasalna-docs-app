// Opens Razorpay checkout for a plan or a batch seat, then asks the server to verify the payment.
(function () {
  var app = document.getElementById('pricing-app');
  if (!app) return;
  var msg = document.getElementById('pricing-msg');
  function say(t) { msg.textContent = t; }

  function post(url, data) {
    return fetch(url, {
      method: 'POST', credentials: 'same-origin', body: new URLSearchParams(data),
      headers: { 'X-CSRFToken': app.dataset.csrf },
    }).then(function (r) { return r.json().then(function (j) { return { ok: r.ok, body: j }; }); });
  }

  function buy(kind, slug, button) {
    if (app.dataset.authed !== '1') { window.location = app.dataset.login; return; }
    button.disabled = true; say('Starting checkout…');
    post(app.dataset.checkout, { kind: kind, slug: slug }).then(function (res) {
      if (!res.ok) { say(res.body.error || 'Could not start checkout.'); button.disabled = false; return; }
      var o = res.body;
      var rzp = new window.Razorpay({
        key: o.key, order_id: o.order_id, amount: o.amount, currency: o.currency, name: o.name,
        description: o.description, prefill: o.prefill,
        handler: function (r) {
          say('Confirming your payment…');
          post(app.dataset.verify, r).then(function (v) {
            if (v.ok && v.body.ok) { say('Payment received. Thank you! Reloading…'); setTimeout(function () { location.reload(); }, 1200); }
            else say('We could not confirm the payment yet. If money was taken, access is added automatically within a few minutes.');
          });
        },
        modal: { ondismiss: function () { button.disabled = false; say(''); } },
      });
      rzp.open();
    }).catch(function () { say('Network problem. Please try again.'); button.disabled = false; });
  }

  app.addEventListener('click', function (e) {
    var b = e.target.closest('[data-buy]');
    if (b && !b.disabled) buy(b.dataset.buy, b.dataset.slug, b);
  });
})();
