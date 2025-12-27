"""
main.py
-------
Main integration script for DevShield AI.
Simulates end-to-end workflow: Developer Guard → AI Risk Engine → Education Engine → Dashboard → Extension.
"""

import sys
import traceback
import requests
from modules.ai_engine.ai_interface import assess_risk
from modules.education.tips import get_educational_message, print_cli_message
from modules.education.policy_rules import check_policy

# Simulate a detected secret from Developer Guard
SIMULATED_SECRET = {
    'file_type': 'py',
    'variable_name': 'API_KEY',
    'pattern_type': 'API Key',
    'entropy': 4.8,
    'filename': 'config.py',
    'line': 42
}

# --- Integration Workflow ---
def main():
    print("\n=== DevShield AI End-to-End Demo ===\n")
    try:
        # 1. Developer Guard detects secret (simulated)
        print(f"[Guard] Detected secret: {SIMULATED_SECRET['pattern_type']} in {SIMULATED_SECRET['filename']} (line {SIMULATED_SECRET['line']})")

        # 2. Send metadata to AI Risk Engine
        ai_result = assess_risk(SIMULATED_SECRET)
        print(f"[AI Risk Engine] Risk Score: {ai_result['risk_score']} | Action: {ai_result['action']}\nExplanation: {ai_result['explanation']}")

        # 3. Education & Policy Engine: policy check and guidance
        policy = check_policy(SIMULATED_SECRET['pattern_type'], {'variable': SIMULATED_SECRET['variable_name']})
        print(f"[Policy Engine] Policy Decision: {policy['action']} | Reason: {policy['reason']}")
        print_cli_message(SIMULATED_SECRET['pattern_type'], {'variable': SIMULATED_SECRET['variable_name']})

        # 4. Dashboard: send event to backend
        dashboard_event = {
            'timestamp': '2025-12-22T12:00:00',
            'secret_type': SIMULATED_SECRET['pattern_type'],
            'risk_score': ai_result['risk_score'],
            'action': ai_result['action'],
            'details': f"{policy['reason']} (File: {SIMULATED_SECRET['filename']}, Line: {SIMULATED_SECRET['line']})"
        }
        try:
            resp = requests.post('http://localhost:5000/api/events', json=dashboard_event, timeout=3)
            if resp.status_code == 201:
                print("[Dashboard] Event sent and visible in dashboard UI.")
            else:
                print(f"[Dashboard] Failed to send event: {resp.text}")
        except Exception as e:
            print(f"[Dashboard] Error sending event: {e}")

        # 5. Extension: simulate alert (console log)
        print(f"[Extension] ALERT: Secret detected in clipboard paste! Type: {SIMULATED_SECRET['pattern_type']} (Redacted: ***)")
        print("\n=== End of Demo ===\n")

    except Exception as e:
        print(f"[ERROR] {e}")
        traceback.print_exc(file=sys.stdout)

if __name__ == "__main__":
    main()
