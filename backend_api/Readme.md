
# DevShield-AI Backend API

> _"The brain behind your coding safety net—risk scoring, policy, and analytics for all DevShield-AI clients."_

This backend powers the [DevShield-AI](../README.md) suite, providing a central API for secret detection, risk scoring, policy enforcement, analytics, and user management.

---

## What It Does

- **Receives secret detection events** from VS Code, browser extension, CLI, and dashboard
- **Scores risk** using AI and rule-based logic
- **Enforces policy** (block, warn, allow)
- **Logs events** for analytics and audit
- **Manages users, API keys, and policies** (admin dashboard)

---

## Getting Started

1. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
2. Start the server:
   ```sh
   python app.py
   ```
3. The API will be available at http://localhost:8000/api/analyze

---

## Example Usage

Send a POST request with JSON:
```
{
  "pattern_type": "API Key",
  "variable_name": "API_KEY",
  "filename": "config.py",
  "line": 42
}
```

Response:
```
{
  "risk_score": 85,
  "action": "block",
  "explanation": "Detected API Key. Risk score: 85. Action: block."
}
```

---

## Integration & Extending

- Connects with all DevShield-AI clients (VS Code, browser, CLI, dashboard)
- Ready for Azure deployment and team onboarding
- See [DevShield-AI main README](../README.md) for full-stack integration

---

**Power up your coding safety net. [Learn more about DevShield-AI →](../README.md)**
