# DevShield-AI: Developer Guard

> _"Stop secrets before they ever leave your machine. DevShield-AI is your last line of defense—right in your Git workflow."_

This module is part of the [DevShield-AI](../../README.md) suite, preventing accidental commits of secrets (API keys, tokens, passwords, etc.) with pre-commit hooks and CLI scanning.

## Folder Structure
```
guard/
├── cli_scanner.py         # CLI tool to scan staged files for secrets
├── pre_commit_hook.py     # Git pre-commit hook template
├── utils.py               # Utility functions (redaction, messages)
└── README.md              # This documentation
```


---

## What It Does

- **Pre-commit hook**: blocks secrets before they hit your repo
- **CLI scanner**: scan staged files for secrets anytime
- **Redacts secrets** in logs for safety
- **Friendly messages**: clear, color-coded warnings and guidance

---

## Getting Started

### 1. Set up the Pre-commit Hook
```sh
cp modules/guard/pre_commit_hook.py .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```
Now, every time you run `git commit`, the scanner will check staged files for secrets.

### 2. Run the CLI Scanner Manually
```sh
python modules/guard/cli_scanner.py
```
Options:
- `--report <file>`: Output scan report (JSON or HTML)
- `--format json|html`: Report format

### 3. Safe Commit Override
If you must commit with secrets (not recommended):
```sh
git commit --allow-secret --justification "Reason for override"
```
Or set environment variables:
```sh
export DEVSHIELD_ALLOW_SECRET=true
export DEVSHIELD_JUSTIFICATION="Reason for override"
```

## Example Outputs

**Blocked Commit:**
```
[WARNING]
Potential secrets detected:
[WARNING] [2025-12-22T15:45:56.088134] DvShield-AI/sample_secret_file.py:2 [API Key] AK********************90 (Entropy: 4.11, Risk: 82)
...
Please remove secrets before committing.
```

**Scan Report (JSON):**
```json
[
	{
		"timestamp": "2025-12-22T15:45:56.088134",
		"file": "DvShield-AI/sample_secret_file.py",
		"line": 2,
		"secret_type": "API Key",
		"redacted": "AK********************90",
		"entropy": 4.11,
		"risk_score": 82
	},
	...
]
```


---

## Demo Scenario (Hackathon Story)
1. Developer tries to commit a secret (e.g., API key in code).
2. Guard blocks the commit and shows a clear warning with details.
3. Developer can override with justification (for emergencies).
4. Scan report and logs are generated for audit.
5. (Integration) AI Risk Engine evaluates risk, Education module explains, Dashboard updates, Extension alerts if pasted.

---


## How It Works

- **Regex patterns**: Detect common secrets (API keys, tokens, passwords, cloud keys, JWTs, etc.)
- **Entropy-based detection**: Flags random-looking strings that may be secrets.
- **Redaction**: Detected secrets are redacted in logs for safety.
- **Friendly messages**: Warnings and errors are color-coded for clarity.
- **Logging**: All findings are logged with timestamp, file, secret type, entropy, and risk score.

---

## Integration & Extending

- Connects with all DevShield-AI clients (VS Code, browser, backend, dashboard)
- Ready for Azure deployment and team onboarding
- See [DevShield-AI main README](../../README.md) for full-stack integration

---

**Stop secrets at the source. [Learn more about DevShield-AI →](../../README.md)**

## Note
- For production, consider advanced secret detection and integration with secret management tools.


API_KEY = "AKIAIOSFODNN7EXAMPLE"
