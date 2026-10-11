/* Job board: ask before destructive actions (forms marked data-confirm). */
document.addEventListener("submit", function (e) {
  var form = e.target.closest("form[data-confirm]");
  if (form && !window.confirm(form.dataset.confirm)) e.preventDefault();
});
