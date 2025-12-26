# DevShield-AI: AI Risk Engine

> _"Is this secret really risky? Let AI decide—and explain why."_

This module is part of the [DevShield-AI](../../README.md) suite, providing automated risk assessment and smart explanations for detected secrets or risky code patterns.

## Folder Structure

```
ai_engine/
├── ai_interface.py     # Handles AI API calls (Azure OpenAI or mock)
├── risk_scoring.py     # Calculates risk score
├── explanation.py      # Generates explanations for developers
└── README.md           # Documentation and usage
```


---

## What It Does

- **Assesses risk** of detected secrets or sensitive patterns (API keys, tokens, etc.)
- **Explains the risk** in plain language for developers
- **Guides action**: block, warn, or allow code based on risk


---

## Getting Started

Test the engine locally:
```sh
python modules/ai_engine/ai_interface.py
```
Runs in local (mock) mode. To use Azure OpenAI, set `use_azure_openai=True` and provide your API key, endpoint, and deployment name.

---

## Integration & Extending

1. From Developer Guard or any DevShield-AI client, collect metadata for each detected secret:
	- file_type (e.g., 'py', 'json')
	- variable_name (e.g., 'API_KEY')
	- pattern_type (e.g., 'API Key', 'Token')
	- entropy (float)
2. Call `assess_risk(metadata)` from `ai_interface.py`.
3. Use the returned `risk_score`, `action` (block/warn/allow), and `explanation` to guide developer workflow.

See [DevShield-AI main README](../../README.md) for full-stack integration.
3. Use the returned `risk_score`, `action` (block/warn/allow), and `explanation` to guide developer workflow.


---

## Example Integration

```python
from modules.ai_engine.ai_interface import assess_risk

metadata = {
	'file_type': 'py',
	'variable_name': 'API_KEY',
	'pattern_type': 'API Key',
	'entropy': 4.7
}
result = assess_risk(metadata)
print(result)
```


---

## Error Handling

- If Azure OpenAI is enabled but fails, the engine will automatically fall back to local rule-based logic and provide a fallback explanation.


---

**Let AI keep your code safe. [Learn more about DevShield-AI →](../../README.md)**
