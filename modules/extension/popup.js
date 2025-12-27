// popup.js
// Handles the popup UI for DevShield AI Guard Extension.
// Shows warning, redaction preview, and Allow/Cancel options.

document.addEventListener('DOMContentLoaded', function () {
  // Listen for secret detection messages from the content script
  window.addEventListener('message', function (event) {
    if (event.data && event.data.type === 'DEVSHIELD_SECRET_DETECTED') {
      showWarning(event.data.original, event.data.redacted, event.data.backend);
    }
  });

  // UI elements
  const warningDiv = document.getElementById('warning');
  const originalDiv = document.getElementById('original');
  const redactedDiv = document.getElementById('redacted');
  const allowBtn = document.getElementById('allow');
  const cancelBtn = document.getElementById('cancel');
  const backendDiv = document.getElementById('backendResponse');

  // Show the warning popup with redaction preview and backend response
  function showWarning(original, redacted, backend) {
    warningDiv.style.display = 'block';
    originalDiv.textContent = original;
    // Highlight the redacted part (asterisks) in red using HTML
    const highlighted = redacted.replace(/(\*{3,})/g, '<span style="color:#d32f2f;font-weight:bold;">$1</span>');
    redactedDiv.innerHTML = highlighted;
    // Show backend response
    if (backendDiv) {
      backendDiv.innerHTML = `<b>DevShield Response:</b> <span style="color:${backendColor(backend)};font-weight:bold;">${backend.action ? backend.action.toUpperCase() : ''}</span><br>${backend.explanation || ''}`;
    }
    warningDiv.style.animation = 'fadeIn 0.5s';
  }

  function backendColor(backend) {
    if (!backend || !backend.action) return '#333';
    if (backend.action === 'block') return '#d32f2f';
    if (backend.action === 'warn') return '#f39c12';
    return '#27ae60';
  }

  // Allow: paste redacted content
  allowBtn.onclick = function () {
    navigator.clipboard.writeText(redactedDiv.textContent).then(() => {
      window.close();
    });
  };

  // Cancel: close popup, do not paste
  cancelBtn.onclick = function () {
    window.close();
  };
});
