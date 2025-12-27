// options.js
// Handles saving and loading of user-configurable secret detection regex patterns for DevShield AI Guard Extension.

// Cross-browser API (browser.* for Firefox, chrome.* for Chrome/Edge)
const extAPI = (typeof browser !== 'undefined') ? browser : chrome;

document.addEventListener('DOMContentLoaded', function () {
  const patternsTextarea = document.getElementById('patterns');
  const statusSpan = document.getElementById('status');
  const form = document.getElementById('rulesForm');

  // Load saved patterns and logging option from storage
  const apikeyInput = document.getElementById('apikey');
  const apikeyForm = document.getElementById('apikeyForm');
  const apikeyStatus = document.getElementById('apikeyStatus');
  extAPI.storage.sync.get(['secretPatterns', 'logToDashboard'], function(result) {
  // Load saved API key
  extAPI.storage.sync.get(['devshieldApiKey'], function(result) {
    if (result.devshieldApiKey) {
      apikeyInput.value = result.devshieldApiKey;
    }
  });

  // Save API key
  apikeyForm.onsubmit = function(e) {
    e.preventDefault();
    const key = apikeyInput.value.trim();
    extAPI.storage.sync.set({ devshieldApiKey: key }, function() {
      apikeyStatus.textContent = 'API Key saved!';
      setTimeout(() => { apikeyStatus.textContent = ''; }, 1200);
    });
  };
    if (result.secretPatterns && Array.isArray(result.secretPatterns)) {
      patternsTextarea.value = result.secretPatterns.join('\n');
    } else {
      // Default patterns
      patternsTextarea.value = [
        'api[_-]?key\\s*[:=]\\s*[\"\']?[A-Za-z0-9\-_=]{16,}[\"\']?',
        'secret[_-]?key\\s*[:=]\\s*[\"\']?[A-Za-z0-9\-_=]{16,}[\"\']?',
        'token\\s*[:=]\\s*[\"\']?[A-Za-z0-9\-_=]{16,}[\"\']?',
        'password\\s*[:=]\\s*[\"\']?.{8,}[\"\']?'
      ].join('\n');
    }
    document.getElementById('logToDashboard').checked = !!result.logToDashboard;
  });

  // Save patterns and logging option to storage
  form.onsubmit = function(e) {
    e.preventDefault();
    const patterns = patternsTextarea.value.split('\n').map(s => s.trim()).filter(Boolean);
    const logToDashboard = document.getElementById('logToDashboard').checked;
    extAPI.storage.sync.set({ secretPatterns: patterns, logToDashboard: logToDashboard }, function() {
      statusSpan.textContent = 'Saved!';
      setTimeout(() => { statusSpan.textContent = ''; }, 1200);
    });
  };
});
