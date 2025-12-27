import json
import os

# Path for notification history and log files (for dashboard integration)
NOTIFICATION_HISTORY_PATH = os.path.join(os.path.dirname(__file__), 'notification_history.json')
LOG_PATH = os.path.join(os.path.dirname(__file__), 'education_log.jsonl')

def load_notification_history():
    """Load notification history from file."""
    if os.path.exists(NOTIFICATION_HISTORY_PATH):
        try:
            with open(NOTIFICATION_HISTORY_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_notification_history(history):
    """Save notification history to file."""
    try:
        with open(NOTIFICATION_HISTORY_PATH, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2)
    except Exception as e:
        print(f"[NotificationHistory] Failed to save: {e}")

def add_notification(secret_type, context=None, status="shown"):
    """
    Add a notification event to history. Status: shown/ignored/acknowledged
    """
    history = load_notification_history()
    entry = {
        "secret_type": secret_type,
        "context": context or {},
        "status": status
    }
    history.append(entry)
    save_notification_history(history)

def update_notification_status(index, status):
    """
    Update the status of a notification by index (e.g., ignored/acknowledged)
    """
    history = load_notification_history()
    if 0 <= index < len(history):
        history[index]["status"] = status
        save_notification_history(history)
        return True
    return False

def get_notification_history():
    """Return the full notification history list."""
    return load_notification_history()

def log_event(event_type, data):
    """
    Log an event (alert/action) to a JSONL file for analytics/dashboard.
    """
    entry = {
        "event_type": event_type,
        "data": data
    }
    try:
        with open(LOG_PATH, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry) + '\n')
    except Exception as e:
        print(f"[EducationLog] Failed to log event: {e}")

def get_educational_message(secret_type, context=None, language='en'):
    """
    Returns an educational message for the given secret type and language.
    Args:
        secret_type (str): e.g. 'API Key', 'Password', 'Token', etc.
        context (dict): Optional, extra info (e.g. filename, variable name)
        language (str): Language code, e.g. 'en', 'hi'
    Returns:
        dict: { 'why_risky': str, 'secure_alternative': str, 'best_practice': str }
    """
    # Multi-language message database (extend as needed)
    messages = {
        'en': {
            'API Key': {
                'why_risky': "API keys grant access to sensitive services. If leaked, attackers can abuse your account or data.",
                'secure_alternative': "Store API keys in environment variables or a secrets manager, never in code.",
                'best_practice': "Use .env files, set permissions, and rotate keys regularly. Never commit secrets to version control."
            },
            'Password': {
                'why_risky': "Passwords in code can be easily extracted and misused, leading to account compromise.",
                'secure_alternative': "Use environment variables or a secrets vault to store passwords.",
                'best_practice': "Never hardcode passwords. Use strong, unique passwords and enable multi-factor authentication."
            },
            'Token': {
                'why_risky': "Tokens can provide direct access to APIs or user data. Leaked tokens can be used for impersonation.",
                'secure_alternative': "Store tokens securely outside of code, e.g., in environment variables.",
                'best_practice': "Limit token scope, set expirations, and rotate tokens regularly."
            },
            'Secret Key': {
                'why_risky': "Secret keys are used for encryption or authentication. Exposure can break security guarantees.",
                'secure_alternative': "Use a secrets manager or environment variables to store secret keys.",
                'best_practice': "Restrict access, rotate keys, and audit usage."
            },
            'OAuth Token': {
                'why_risky': "OAuth tokens can be used to impersonate users or access protected resources.",
                'secure_alternative': "Store OAuth tokens in secure storage, never in code or public repos.",
                'best_practice': "Use short-lived tokens, refresh regularly, and monitor for leaks."
            },
            'Private Key': {
                'why_risky': "Private keys are used for authentication and encryption. Leaked keys can compromise entire systems.",
                'secure_alternative': "Store private keys in secure vaults or hardware security modules.",
                'best_practice': "Never share private keys. Use passphrases and restrict access."
            },
            'Database Connection String': {
                'why_risky': "Connection strings often contain credentials and host info. Leaks can lead to data breaches.",
                'secure_alternative': "Use environment variables or secret managers for connection strings.",
                'best_practice': "Limit DB user permissions, rotate credentials, and audit access."
            },
            'AWS Secret Access Key': {
                'why_risky': "AWS keys grant access to cloud resources. Leaked keys can result in major breaches and costs.",
                'secure_alternative': "Use IAM roles and environment variables, never hardcode AWS keys.",
                'best_practice': "Rotate keys, use least privilege, and enable CloudTrail monitoring."
            },
            'JWT': {
                'why_risky': "JWTs can be used to impersonate users or escalate privileges if leaked.",
                'secure_alternative': "Store JWTs securely in HTTP-only cookies or secure storage.",
                'best_practice': "Set short expirations, use strong signing keys, and validate tokens."
            },
            'Hardcoded IP Address': {
                'why_risky': "Hardcoded IPs can make systems brittle and expose internal infrastructure.",
                'secure_alternative': "Use configuration files or environment variables for endpoints.",
                'best_practice': "Document endpoints, avoid hardcoding, and use DNS where possible."
            },
            'Hardcoded Email': {
                'why_risky': "Hardcoded emails can leak user info and are hard to update.",
                'secure_alternative': "Store emails in config or environment variables.",
                'best_practice': "Avoid hardcoding PII. Use placeholders in code."
            },
            'Default': {
                'why_risky': "Sensitive values in code can be discovered and exploited.",
                'secure_alternative': "Store all secrets outside of codebase.",
                'best_practice': "Scan code for secrets before committing."
            }
        },
        # Example for Hindi (extend as needed)
        'hi': {
            'API Key': {
                'why_risky': "API कुंजी संवेदनशील सेवाओं तक पहुँच प्रदान करती है। यदि लीक हो जाए, तो हमलावर आपके खाते या डेटा का दुरुपयोग कर सकते हैं।",
                'secure_alternative': "API कुंजी कोड में नहीं, बल्कि environment variables या secrets manager में रखें।",
                'best_practice': ".env फ़ाइलें उपयोग करें, अनुमतियाँ सेट करें, और नियमित रूप से कुंजी बदलें। कभी भी secrets को version control में न डालें।"
            },
            'Default': {
                'why_risky': "कोड में संवेदनशील मान पाए जाने और दुरुपयोग की संभावना होती है।",
                'secure_alternative': "सभी secrets को कोडबेस के बाहर रखें।",
                'best_practice': "commit करने से पहले कोड को secrets के लिए स्कैन करें।"
            }
        }
    }
    lang_msgs = messages.get(language, messages['en'])
    msg = lang_msgs.get(secret_type, lang_msgs['Default'])
    if context and 'variable' in context:
        msg = msg.copy()
        msg['why_risky'] += f" (Found in variable: {context['variable']})"
    return msg

def print_cli_message(secret_type, context=None, language='en'):
    """
    Print educational message in CLI style.
    """
    msg = get_educational_message(secret_type, context, language)
    print("\n=== DevShield Security Education ===")
    print(f"Why risky: {msg['why_risky']}")
    print(f"Secure alternative: {msg['secure_alternative']}")
    print(f"Best practice: {msg['best_practice']}")
    print("====================================\n")
    add_notification(secret_type, context, status="shown")
    log_event("alert_shown", {"secret_type": secret_type, "context": context, "language": language})

def get_popup_message(secret_type, context=None, language='en'):
    """
    Return a formatted string for popup display (e.g., browser/extension).
    """
    msg = get_educational_message(secret_type, context, language)
    return (f"⚠️ <b>Why risky:</b> {msg['why_risky']}<br>"
            f"<b>Secure alternative:</b> {msg['secure_alternative']}<br>"
            f"<b>Best practice:</b> {msg['best_practice']}")

# Example usage
if __name__ == "__main__":
    # Simulate receiving a secret detection from Guard/AI Engine
    print_cli_message('API Key', {'variable': 'MY_API_KEY'}, language='en')
    print(get_popup_message('Password', {'variable': 'DB_PASS'}, language='en'))
    # Mark first notification as acknowledged
    update_notification_status(0, "acknowledged")
    # Print notification history
    print("Notification history:")
    for i, entry in enumerate(get_notification_history()):
        print(f"{i}: {entry}")
