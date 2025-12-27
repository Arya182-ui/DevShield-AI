"""
explanation.py
--------------
Generates brief, actionable explanations for risk decisions in the AI Risk Engine.
"""

def generate_explanation(metadata, risk_score):

    """
    Generate a human-readable, actionable explanation for the developer based on metadata and risk score.
    Args:
        metadata (dict): Info from Developer Guard (file_type, variable_name, pattern_type, entropy)
        risk_score (int or dict): Calculated risk score (0-100) or dict with severity/confidence
    Returns:
        str: Explanation
    """
    pattern = metadata.get('pattern_type', 'Unknown')
    file_type = metadata.get('file_type', 'file')
    variable = metadata.get('variable_name', '')
    entropy = metadata.get('entropy', 0)
    # Support risk_score as dict
    if isinstance(risk_score, dict):
        score = risk_score.get('risk_score', 0)
        severity = risk_score.get('severity', None)
        confidence = risk_score.get('confidence', None)
    else:
        score = risk_score
        severity = None
        confidence = None

    if score >= 80:
        msg = (f"🚨 High risk: {pattern} detected in {file_type} (variable: {variable}). "
               f"This value appears highly sensitive (entropy={entropy:.2f}). Commit is blocked to protect your project.")
    elif score >= 40:
        msg = (f"⚠️ Moderate risk: Potential sensitive value '{variable}' in {file_type} (pattern: {pattern}). "
               f"Entropy={entropy:.2f}. Please review and consider moving secrets to environment variables or a vault.")
    else:
        msg = (f"✅ Low risk: No sensitive patterns detected in {file_type}. Safe to proceed.")

    if severity or confidence:
        msg += f"\n[Severity: {severity or 'n/a'} | Confidence: {confidence if confidence is not None else 'n/a'}]"
    return msg

# Example usage
if __name__ == "__main__":
    test_metadata = {
        'file_type': 'py',
        'variable_name': 'API_KEY',
        'pattern_type': 'API Key',
        'entropy': 4.9
    }
    print(generate_explanation(test_metadata, 85))
