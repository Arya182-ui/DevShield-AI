"""
risk_scoring.py
---------------
Risk scoring logic for DevShield AI Risk Engine.
Receives metadata and calculates a risk score (0-100).
"""


def calculate_risk_score(metadata):
    """
    Calculate a risk score (0-100) based on metadata from Developer Guard.
    Uses context, pattern weights, and entropy for nuanced scoring.
    Returns dict with score, severity, and confidence.
    """
    score = 0
    # Pattern weights (more granular)
    pattern_weights = {
        'api key': 60,
        'token': 50,
        'password': 70,
        'secret': 60,
        'access_key': 60,
        'private_key': 80,
        'aws access key id': 80,
        'aws secret access key': 90,
        'google api key': 70,
        'jwt': 60,
        'database password': 80,
        'cloud provider secret': 70,
        'high-entropy string': 40
    }
    risky_var_names = ['api_key', 'token', 'password', 'secret', 'access_key', 'private_key']
    risky_file_types = ['env', 'json', 'yml', 'yaml', 'ini', 'config']

    pattern_type = metadata.get('pattern_type', '').lower()
    variable_name = metadata.get('variable_name', '').lower()
    file_type = metadata.get('file_type', '').lower()
    entropy = metadata.get('entropy', 0)

    # Add score for pattern type
    for key, weight in pattern_weights.items():
        if key in pattern_type:
            score += weight
            break

    # Add score for risky variable name
    for risky in risky_var_names:
        if risky in variable_name:
            score += 15
            break

    # Add score for risky file type
    for risky_ft in risky_file_types:
        if risky_ft in file_type:
            score += 10
            break

    # Add score for entropy (weighted)
    if entropy > 5.0:
        score += 25
    elif entropy > 4.5:
        score += 15
    elif entropy > 4.0:
        score += 7

    # Cap score at 100
    score = min(score, 100)

    # Severity and confidence
    if score >= 80:
        severity = 'critical'
        confidence = 0.95
    elif score >= 60:
        severity = 'high'
        confidence = 0.85
    elif score >= 40:
        severity = 'medium'
        confidence = 0.7
    elif score >= 20:
        severity = 'low'
        confidence = 0.5
    else:
        severity = 'info'
        confidence = 0.3

    return {
        'risk_score': score,
        'severity': severity,
        'confidence': confidence
    }

# Example usage
if __name__ == "__main__":
    test_metadata = {
        'file_type': 'py',
        'variable_name': 'SECRET',
        'pattern_type': 'Token',
        'entropy': 4.8
    }
    print("Risk score:", calculate_risk_score(test_metadata))
