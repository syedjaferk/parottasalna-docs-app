// Google Analytics 4 for the portal and every course's docs pages.
// The Measurement ID comes from the script tag (data-ga-id), set by GA_MEASUREMENT_ID in settings.
(function () {
  var script = document.currentScript;
  var GA_ID = script && script.getAttribute("data-ga-id");
  if (!GA_ID || !/^G-[A-Z0-9]+$/.test(GA_ID)) return;

  // Never count local previews.
  if (/^(localhost|127\.0\.0\.1|\[::1\])$/.test(location.hostname) || location.protocol === "file:") return;
  // Respect "don't track me" browser settings (Global Privacy Control, Do Not Track).
  if (navigator.globalPrivacyControl === true || navigator.doNotTrack === "1" || window.doNotTrack === "1") return;

  var tag = document.createElement("script");
  tag.async = true;
  tag.src = "https://www.googletagmanager.com/gtag/js?id=" + GA_ID;
  document.head.appendChild(tag);

  window.dataLayer = window.dataLayer || [];
  window.gtag = function () { window.dataLayer.push(arguments); };
  window.gtag("js", new Date());
  // Measurement only: no Google signals, no ad personalisation.
  window.gtag("config", GA_ID, {
    allow_google_signals: false,
    allow_ad_personalization_signals: false
  });
})();
