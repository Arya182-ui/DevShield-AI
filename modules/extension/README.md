# DevShield-AI Browser Extension

> _"Ever pasted a secret into ChatGPT or Copilot? DevShield-AI has your back—even in the browser."_

This extension is part of the [DevShield-AI](../../README.md) suite, protecting you from accidental secret leaks in web-based coding tools.

---

## What It Does

- **Scans pasted content** in browser textareas/inputs for secrets (API keys, tokens, passwords)
- **Blocks risky pastes** and shows a friendly popup with redacted preview and guidance
- **Works locally**—no data leaves your machine
- **Seamless onboarding**: Enter your API key once for full protection (see [main README](../../README.md#how-to-get-started))

---


## Folder Structure
```
extension/
├── background.js   # Listens for paste events, scans for secrets
├── popup.js        # Handles popup UI and redaction preview
├── popup.html      # Popup UI layout
├── manifest.json   # Chrome/Edge extension manifest
└── README.md       # This documentation
```


## Getting Started
1. Open Chrome/Edge and go to `chrome://extensions` or `edge://extensions`.
2. Enable "Developer mode" (top right).
3. Click "Load unpacked" and select the `modules/extension/` folder.
4. The DevShield-AI icon should appear in your browser.
5. Enter your API key in the options page (see [main README](../../README.md#how-to-get-started)).


---

## How It Works

1. **Paste code** into any web tool (ChatGPT, Copilot, etc.)
2. Extension scans for secrets using Developer Guard patterns
3. If a secret is found, paste is blocked and a popup appears:
    - See original and redacted content
    - Choose to allow (redacted) or cancel
4. All scanning is local—your data stays private


---

## Integration & Extending

- Uses the same secret detection patterns as Developer Guard
- Can be extended to communicate with the main DevShield-AI backend for analytics, policy, and team management
- See [DevShield-AI main README](../../README.md) for full-stack integration


---

**Protect your secrets everywhere you code. [Learn more about DevShield-AI →](../../README.md)**
