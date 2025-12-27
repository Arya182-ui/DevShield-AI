# DevShield-AI VS Code Extension

> _"Ever pasted an API key by accident? DevShield-AI is your coding safety net—right inside VS Code."_

This extension is part of the [DevShield-AI](../../README.md) suite, providing real-time secret detection and friendly guidance as you code.

---

## What It Does

- **Scans your code** on save and paste for secrets (API keys, tokens, passwords)
- **Warns you instantly** with popups and explanations
- **Manual scan**: Run "DevShield: Scan Document for Secrets" from the Command Palette
- **Seamless onboarding**: Register/login once, and your API key keeps you protected

---

## Getting Started

1. Open `modules/vscode-extension` in VS Code.
2. Run `npm install` if needed.
3. Press F5 to launch the extension in a new Extension Development Host window.
4. Register/login with your DevShield-AI account (see [main README](../../README.md#how-to-get-started)).
5. Paste or save code with secrets (e.g., `API_KEY = "abcd1234secret5678"`).
6. See instant warnings and helpful tips if secrets are detected.

---

## Extending & Integrating

- Add new secret patterns in `extension.js` for more coverage
- Integrate with the backend API for analytics, policy, and team management
- See [DevShield-AI main README](../../README.md) for full-stack integration

---

**Protect your code. Ship without secrets. [Learn more about DevShield-AI →](../../README.md)**
