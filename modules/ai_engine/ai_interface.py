"""
ai_interface.py
--------------
Handles AI API calls (Azure OpenAI or local mock) for risk assessment.
Imports risk scoring and explanation modules for modular workflow.
"""

import os
import requests
from .risk_scoring import calculate_risk_score
from .explanation import generate_explanation

def assess_risk(metadata, use_azure_openai=False, azure_api_key=None, azure_endpoint=None, deployment_name=None):
    try:
        if use_azure_openai:
            # Load from environment if not provided
            azure_api_key = azure_api_key or os.getenv('AZURE_OPENAI_API_KEY')
            azure_endpoint = azure_endpoint or os.getenv('AZURE_OPENAI_ENDPOINT')
            deployment_name = deployment_name or os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME')
            if not (azure_api_key and azure_endpoint and deployment_name):
                raise ValueError("Azure OpenAI API key, endpoint, and deployment name are required (either as arguments or environment variables).")
            headers = {
                "api-key": azure_api_key,
                "Content-Type": "application/json"
            }
            prompt = (
                f"You are a security risk engine. Given the following metadata, "
                f"return a JSON with risk_score (0-100), action (block/warn/allow), and explanation.\n"
                f"Metadata: {metadata}"
            )
            data = {
                "messages": [
                    {"role": "system", "content": "You are a security risk engine."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 200,
                "temperature": 0.2
            }
            url = f"{azure_endpoint}/openai/deployments/{deployment_name}/chat/completions?api-version=2023-03-15-preview"
            response = requests.post(url, headers=headers, json=data, timeout=10)
            response.raise_for_status()
            result = response.json()
            # Parse the response (assume model returns a JSON string in 'content')
            content = result['choices'][0]['message']['content']
            import json as _json
            parsed = _json.loads(content)
            risk_score = int(parsed.get('risk_score', 0))
            action = parsed.get('action', 'allow')
            explanation = parsed.get('explanation', 'No explanation provided.')
            return {
                'risk_score': risk_score,
                'action': action,
                'explanation': explanation
            }
        else:
            local = calculate_risk_score(metadata)
            return {
                'risk_score': local['risk_score'],
                'action': _decide_action(local['risk_score']),
                'explanation': generate_explanation(metadata, local['risk_score'])
            }
    except Exception as e:
        return {
            'risk_score': 0,
            'action': 'allow',
            'explanation': f'Error in risk assessment: {e}'
        }

def _decide_action(risk_score):
    """
    Decide action based on risk score.
    Args:
        risk_score (int): 0-100
    Returns:
        str: 'block', 'warn', or 'allow'
    """
    if risk_score >= 80:
        return 'block'
    elif risk_score >= 40:
        return 'warn'
    else:
        return 'allow'

# Example usage
if __name__ == "__main__":
    # Example metadata
    test_metadata = {
        'file_type': 'py',
        'variable_name': 'API_KEY',
        'pattern_type': 'API Key',
        'entropy': 4.7
    }
    # Local mode
    print("Local risk assessment:")
    print(assess_risk(test_metadata))
    # Azure OpenAI mode (will fallback if not configured)
    # print(assess_risk(test_metadata, use_azure_openai=True, azure_api_key='YOUR_KEY', azure_endpoint='YOUR_ENDPOINT', deployment_name='YOUR_DEPLOYMENT'))
