// Admin > Assessments: "Copy link" buttons copy the full address students should open.
(function () {
  function absolute(path) { return window.location.origin + path; }

  function copy(text, button) {
    var done = function () {
      var old = button.textContent;
      button.textContent = 'Copied!';
      setTimeout(function () { button.textContent = old; }, 1500);
    };
    if (navigator.clipboard && window.isSecureContext) {
      navigator.clipboard.writeText(text).then(done, function () { window.prompt('Copy this link:', text); });
    } else {
      window.prompt('Copy this link:', text);   // plain http (local network) has no clipboard API
    }
  }

  document.addEventListener('click', function (event) {
    var button = event.target.closest('[data-copy-share]');
    if (!button) return;
    event.preventDefault();
    copy(absolute(button.getAttribute('data-copy-share')), button);
  });

  // Show the full address (not just the path) next to the button on the edit page.
  document.querySelectorAll('[data-share-path]').forEach(function (code) {
    code.textContent = absolute(code.getAttribute('data-share-path'));
  });
})();
