// background.js
// Listens for paste events in browser textareas/inputs and scans for secrets using Developer Guard patterns.
// If a secret is detected, shows a warning popup with redaction preview.

// Cross-browser API (browser.* for Firefox, chrome.* for Chrome/Edge)
const extAPI = (typeof browser !== 'undefined') ? browser : chrome;

// Load secret patterns from storage (user-configurable)
let SECRET_PATTERNS = [];
const DEFAULT_PATTERNS = [
  'api[_-]?key\\s*[:=]\\s*[\"\']?[A-Za-z0-9\-_=]{16,}[\"\']?',
  'secret[_-]?key\\s*[:=]\\s*[\"\']?[A-Za-z0-9\-_=]{16,}[\"\']?',
  'token\\s*[:=]\\s*[\"\']?[A-Za-z0-9\-_=]{16,}[\"\']?',
  'password\\s*[:=]\\s*[\"\']?.{8,}[\"\']?'
];

function loadPatterns(callback) {
  if (extAPI && extAPI.storage && extAPI.storage.sync) {
    extAPI.storage.sync.get(['secretPatterns'], function(result) {
      let patterns = result.secretPatterns && Array.isArray(result.secretPatterns) && result.secretPatterns.length > 0
        ? result.secretPatterns : DEFAULT_PATTERNS;
      SECRET_PATTERNS = patterns.map(p => new RegExp(p, 'i'));
      if (callback) callback();
    });
  } else {
    SECRET_PATTERNS = DEFAULT_PATTERNS.map(p => new RegExp(p, 'i'));
    if (callback) callback();
  }
}

// Redact a detected secret for preview
function redactSecret(str) {
  return str.replace(/[A-Za-z0-9\-_=]{8,}/g, (match) => {
    if (match.length <= 4) return '*'.repeat(match.length);
    return match.slice(0, 2) + '*'.repeat(match.length - 4) + match.slice(-2);
  });
}

// Listen for paste events on all textareas and inputs
function listenForPasteEvents() {
  document.addEventListener('paste', function(event) {
    let pastedData = (event.clipboardData || window.clipboardData).getData('text');
    // Ensure patterns are loaded before checking
    if (!SECRET_PATTERNS.length) {
      loadPatterns(() => checkPaste(event, pastedData));
    } else {
      checkPaste(event, pastedData);
    }
  }, true);
}


async function checkPaste(event, pastedData) {
  let found = false;
  let redacted = pastedData;
  let matchedType = 'Secret';
  for (const pattern of SECRET_PATTERNS) {
    if (pattern.test(pastedData)) {
      found = true;
      redacted = redactSecret(pastedData);
      if (pattern.source.includes('api')) matchedType = 'API Key';
      else if (pattern.source.includes('token')) matchedType = 'Token';
      else if (pattern.source.includes('password')) matchedType = 'Password';
      else if (pattern.source.includes('secret')) matchedType = 'Secret Key';
      break;
    }
  }
  if (found) {
    event.preventDefault();
    // Get API key from storage
    let apiKey = '';
    if (extAPI && extAPI.storage && extAPI.storage.sync) {
      await new Promise(resolve => {
        extAPI.storage.sync.get(['devshieldApiKey'], function(result) {
          apiKey = result.devshieldApiKey || '';
          resolve();
        });
      });
    }
    // Send to backend for analysis
    let backendResponse = null;
    try {
      const res = await fetch('http://localhost:8000/api/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': apiKey
        },
        body: JSON.stringify({
          pattern_type: matchedType,
          variable_name: pastedData,
          filename: 'browser',
          line: 1
        })
      });
      backendResponse = await res.json();
    } catch (err) {
      backendResponse = { action: 'warn', explanation: 'Backend error: ' + err.message };
    }
    // Send message to popup to show backend response
    window.postMessage({
      type: 'DEVSHIELD_SECRET_DETECTED',
      original: pastedData,
      redacted: redacted,
      backend: backendResponse
    }, '*');
  }
}

// Inject the listener into the page
if (typeof window !== 'undefined') {
  loadPatterns(listenForPasteEvents);
}
