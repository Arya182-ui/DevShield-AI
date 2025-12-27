"""
policy_rules.py
--------------
Simple policy enforcement engine for DevShield AI.
Defines and checks security policies for detected secrets.
"""

import json
import os

def load_policy_config(config_path=None):
    """
    Loads policy config from a JSON file. If not found, uses default rules.
    """
    default_config = {
        "block_types": ["Password", "Secret Key"],
        "warn_types": ["API Key", "Token"],
        "enforce_env": True
    }
    if config_path and os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[PolicyConfig] Failed to load config: {e}. Using default policy.")
    return default_config

def check_policy(secret_type, context=None, config_path=None):
    """
    Checks policy for a detected secret type, using optional config file.
    Args:
        secret_type (str): e.g. 'API Key', 'Password', etc.
        context (dict): Optional, extra info (e.g. filename, variable name)
        config_path (str): Optional path to policy config JSON
    Returns:
        dict: { 'action': 'block'|'warn'|'allow', 'reason': str }
    """
    config = load_policy_config(config_path)
    block_types = config.get('block_types', [])
    warn_types = config.get('warn_types', [])
    enforce_env = config.get('enforce_env', True)

    # Block: must not be committed
    if secret_type in block_types:
        return {'action': 'block', 'reason': f"{secret_type} must never be committed to code."}
    # Warn: allow override, but recommend env vars
    elif secret_type in warn_types:
        return {'action': 'warn', 'reason': f"{secret_type} detected. Strongly recommend using environment variables."}
    # Enforce: all secrets should use env vars
    elif enforce_env:
        return {'action': 'warn', 'reason': "All secrets should be stored in environment variables."}
    else:
        return {'action': 'allow', 'reason': "No policy violation."}

# Example usage
if __name__ == "__main__":
    # Optionally specify a config file path
    config_file = os.path.join(os.path.dirname(__file__), 'policy_config.json')
    print(check_policy('Password', {'variable': 'DB_PASS'}, config_file))
    print(check_policy('API Key', {'variable': 'MY_API_KEY'}, config_file))
    print(check_policy('OtherSecret', {'variable': 'FOO'}, config_file))
