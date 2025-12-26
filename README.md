# DevShield-AI: Your Coding Safety Net

## Imagine this…

You’re working late, racing to finish a feature. You copy-paste some code, commit your changes, and push to GitHub. The next morning, you get an urgent message: “Did you mean to push your API key to the repo?”

**DevShield-AI** is here to make sure that never happens again.

---

## What is DevShield-AI?

DevShield-AI is your friendly, always-on security companion for coding. It watches your back in VS Code, your browser, and even your Git commits—catching secrets before they leak, and helping you fix them instantly.

---

## Why You’ll Love It

- **Real-time protection**: Get instant warnings in VS Code, your browser, or the terminal if you accidentally type or paste a secret.
- **One-click onboarding**: Register or log in once, and your API key keeps you protected everywhere.
- **Smart, human feedback**: Not just “block”—DevShield explains why, and how to fix it.
- **Admin dashboard**: See analytics, manage users, and update policies with a few clicks.
- **Built for Microsoft tech**: Runs on Azure, integrates with VS Code, and is ready for your team.

---

## A Day in the Life (User Story)

1. **You start coding in VS Code.**
   - DevShield-AI quietly checks your code for secrets as you type, save, or commit.
2. **You paste a config file in your browser.**
   - The browser extension pops up: “Whoa! That looks like an API key. Here’s why you should keep it secret.”
3. **You try to commit a password.**
   - The CLI/pre-commit hook blocks the commit, explains the risk, and helps you fix it.
4. **You check the dashboard.**
   - See how many secrets were caught, who needs help, and update your team’s security policy.

---

## Features at a Glance

- **VS Code Extension**: Real-time secret detection, onboarding, and notifications.
- **Browser Extension**: Protects you in ChatGPT, Copilot, and other web tools.
- **CLI/Pre-commit**: Stops secrets before they hit your repo.
- **Backend API**: Central brain for risk scoring, policy, and analytics (Azure-ready).
- **Admin Dashboard**: Analytics, user management, and policy control.

---


## Azure OpenAI Integration Setup

DevShield-AI can leverage Azure OpenAI for advanced risk assessment. To enable this:

1. **Set up Azure OpenAI credentials**
   - Copy `.env.example` to `.env` in the project root.
   - Fill in your Azure OpenAI API key, endpoint, and deployment name:
     ```env
     AZURE_OPENAI_API_KEY=your-azure-openai-api-key
     AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com
     AZURE_OPENAI_DEPLOYMENT_NAME=your-deployment-name
     ```
   - Alternatively, set these as system environment variables.

2. **How it works**
   - The AI engine will automatically use these credentials if you call `assess_risk(..., use_azure_openai=True)` in your code or via the backend.
   - If credentials are not provided as function arguments, they are loaded from environment variables.

3. **Example usage**
   ```python
   from modules.ai_engine.ai_interface import assess_risk
   metadata = {
       'file_type': 'py',
       'variable_name': 'API_KEY',
       'pattern_type': 'API Key',
       'entropy': 4.7
   }
   result = assess_risk(metadata, use_azure_openai=True)
   print(result)
   ```

---

## How to Get Started

### 1. Backend/API
```sh
cd backend_api
pip install -r requirements.txt
python init_db.py
python app.py
# API runs at http://localhost:8000
```

### 2. VS Code Extension
- Open `modules/vscode-extension` in VS Code.
- Run `npm install` if needed.
- Press F5 to launch the extension.
- Register/login, then start coding—DevShield does the rest!

### 3. Browser Extension
- Go to `chrome://extensions` or `edge://extensions`.
- Enable Developer Mode, load `modules/extension/` as unpacked.
- Enter your API key in the options page.
- Paste code in any web tool—DevShield will protect you.

### 4. Dashboard
```sh
cd dashboard_web
python app.py
# Visit http://localhost:5050 for analytics and admin tools
```

---

## How It Works (Behind the Scenes)

1. **Secret detected** (in IDE, browser, or CLI)
2. **Sent to backend** for risk scoring and policy check
3. **User gets feedback** (block, warn, allow—with explanation)
4. **Event logged** for analytics and audit
5. **Admins manage** users and policies in the dashboard


---

## FAQ & Troubleshooting

**Q: I get blocked for pasting a secret. What do I do?**
A: DevShield will show you what’s risky and how to fix it—move secrets to environment variables or a vault.

**Q: How do I reset my API key?**
A: Use the settings page in the extension or dashboard to generate a new one.

**Q: Can I use this with my team?**
A: Yes! Admins can add users and set policies in the dashboard.

**Q: What Microsoft tech does this use?**
A: Azure-ready backend, VS Code extension, and more—built for the Microsoft ecosystem.

---


---

## Learn More: Module Documentation

- [VS Code Extension](modules/vscode-extension/README.md)
- [Browser Extension](modules/extension/README.md)
- [Backend API](backend_api/README.md)
- [Dashboard & Backend](modules/dashboard/README.md)
- [AI Risk Engine](modules/ai_engine/README.md)
- [Education & Policy Engine](modules/education/README.md)
- [Developer Guard (CLI/Pre-commit)](modules/guard/README.md)

---

**DevShield-AI: Code with confidence. Ship without secrets.**
