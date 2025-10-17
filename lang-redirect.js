// Language detection and redirect script for ReadSage
(function() {
  const supportedLangs = ['en', 'es', 'fr', 'pt', 'ru', 'uk', 'tr', 'de'];
  const defaultLang = 'en';

  // Check if we're already on a language page
  const currentPath = window.location.pathname;
  if (currentPath.match(/^\/(en|es|fr|pt|ru|uk|tr|de)\//)) {
    // Already on a language page, don't redirect
    return;
  }

  // Check for saved language preference
  const savedLang = localStorage.getItem('preferred-lang');

  if (savedLang && supportedLangs.includes(savedLang)) {
    window.location.href = '/' + savedLang + '/';
    return;
  }

  // Detect browser language
  const browserLang = navigator.language || navigator.userLanguage;
  const langCode = browserLang.substring(0, 2).toLowerCase();

  // Redirect to appropriate language
  if (supportedLangs.includes(langCode)) {
    window.location.href = '/' + langCode + '/';
  } else {
    window.location.href = '/' + defaultLang + '/';
  }
})();

// Language switcher function
function switchLanguage(lang) {
  localStorage.setItem('preferred-lang', lang);
  window.location.href = '/' + lang + '/';
}
