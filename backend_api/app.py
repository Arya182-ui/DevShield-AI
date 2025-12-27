"""
backend_api/app.py
------------------
Flask backend API for DevShield-AI extension integration.
Provides endpoints for secret detection, risk scoring, and policy checks.
"""

import hashlib
import secrets
from flask import Flask, request, jsonify
from flask import g
from functools import wraps
import time
import sys
import os
import json
import sqlite3
from datetime import datetime

# Ensure project root is in sys.path for module imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from modules.ai_engine.ai_interface import assess_risk
from modules.ai_engine.explanation import generate_explanation
from modules.education.policy_rules import check_policy
import csv
from io import StringIO


sys.path.append('../modules/ai_engine')
sys.path.append('../modules/education')
RATE_LIMIT = 60  
rate_limit_cache = {}
app = Flask(__name__)

def rate_limiter(endpoint):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            api_key = request.headers.get('X-API-Key', 'anon')
            now = int(time.time() // 60)  # current minute
            key = f"{api_key}:{endpoint}:{now}"
            count = rate_limit_cache.get(key, 0)
            if count >= RATE_LIMIT:
                return jsonify({'error': 'Rate limit exceeded. Try again later.'}), 429
            rate_limit_cache[key] = count + 1
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Log file path
LOG_PATH = os.path.join(os.path.dirname(__file__), 'analysis_log.jsonl')


def log_analysis(request_data, response_data):
    entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'request': json.dumps(request_data),
        'response': json.dumps(response_data)
    }
    try:
        conn = get_db()
        conn.execute('INSERT INTO analysis_log (timestamp, request, response) VALUES (?, ?, ?)',
                     (entry['timestamp'], entry['request'], entry['response']))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[LOG] Failed to write log: {e}")


# User management (SQLite)
def get_db():
    db_url = os.environ.get('DEVSHIELD_DB_URL')
    if db_url:
        # Example: 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=...;DATABASE=...;UID=...;PWD=...'
        import pyodbc
        conn = pyodbc.connect(db_url)
        conn.row_factory = None  # pyodbc returns tuples, not dicts
        return conn
    else:
        DB_PATH = os.path.join(os.path.dirname(__file__), 'devshield.db')
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
def load_users():
    conn = get_db()
    users = [dict(row) for row in conn.execute('SELECT username, api_key, role FROM users')]
    conn.close()
    return users
def save_user(username, api_key, role):
    conn = get_db()
    conn.execute('INSERT INTO users (username, api_key, role) VALUES (?, ?, ?)', (username, api_key, role))
    conn.commit()
    conn.close()
def delete_user(username):
    conn = get_db()
    conn.execute('DELETE FROM users WHERE username = ?', (username,))
    conn.commit()
    conn.close()
def get_api_keys():
    conn = get_db()
    keys = {row['api_key'] for row in conn.execute('SELECT api_key FROM users')}
    conn.close()
    return keys

def require_api_key(func):
    from functools import wraps
    @wraps(func)
    def wrapper(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if api_key not in get_api_keys():
            return jsonify({"error": "Unauthorized. Valid API key required."}), 401
        return func(*args, **kwargs)
    return wrapper

@app.route('/api/audit/export', methods=['GET'])
@require_api_key
def export_audit():
    format = request.args.get('format', 'json')
    conn = get_db()
    rows = conn.execute('SELECT timestamp, request, response FROM analysis_log ORDER BY id DESC').fetchall()
    conn.close()
    events = []
    for row in rows:
        try:
            event = {
                'timestamp': row['timestamp'],
                'request': row['request'],
                'response': row['response']
            }
            events.append(event)
        except Exception:
            continue
    if format == 'csv':
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=['timestamp', 'request', 'response'])
        writer.writeheader()
        for e in events:
            writer.writerow(e)
        return output.getvalue(), 200, {'Content-Type': 'text/csv'}
    else:
        return jsonify({'events': events})

# Login endpoint
@app.route('/api/login', methods=['POST'])
def login_user():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({'error': 'Email and password required.'}), 400
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    conn.close()
    if not user:
        return jsonify({'error': 'User not found.'}), 404
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    if user['password_hash'] != password_hash:
        return jsonify({'error': 'Incorrect password.'}), 401
    # No approval check
    return jsonify({'api_key': user['api_key'], 'username': user['username'], 'role': user['role']})

# Admin: list pending users
@app.route('/api/admin/pending_users', methods=['GET'])
@require_api_key
def list_pending_users():
    conn = get_db()
    users = [dict(row) for row in conn.execute('SELECT username, email, role FROM users WHERE approved = 0')]
    conn.close()
    return jsonify({'pending_users': users})

# Admin: approve user
@app.route('/api/admin/approve_user', methods=['POST'])
@require_api_key
def approve_user():
    data = request.get_json()
    email = data.get('email')
    if not email:
        return jsonify({'error': 'Email required.'}), 400
    conn = get_db()
    conn.execute('UPDATE users SET approved = 1 WHERE email = ?', (email,))
    conn.commit()
    conn.close()
    return jsonify({'message': f'User {email} approved.'})

# Admin: reject/delete user
@app.route('/api/admin/reject_user', methods=['POST'])
@require_api_key
def reject_user():
    data = request.get_json()
    email = data.get('email')
    if not email:
        return jsonify({'error': 'Email required.'}), 400
    conn = get_db()
    conn.execute('DELETE FROM users WHERE email = ?', (email,))
    conn.commit()
    conn.close()
    return jsonify({'message': f'User {email} rejected and deleted.'})

@app.route('/api/register', methods=['POST'])
def register_user():
    data = request.get_json()
    username = data.get('username')
    role = data.get('role', 'user')
    if not username:
        return jsonify({'error': 'Username required.'}), 400
    # Check for duplicate username
    conn = get_db()
    exists = conn.execute('SELECT 1 FROM users WHERE username = ?', (username,)).fetchone()
    if exists:
        conn.close()
        return jsonify({'error': 'Username already exists.'}), 400
    import secrets
    api_key = secrets.token_hex(16)
    conn.execute('INSERT INTO users (username, api_key, role) VALUES (?, ?, ?)', (username, api_key, role))
    conn.commit()
    conn.close()
    return jsonify({'username': username, 'api_key': api_key, 'role': role})


@app.route('/api/users', methods=['GET'])
@require_api_key
def list_users():
    users = load_users()
    for u in users:
        u.pop('api_key', None)  # Hide API keys in list
    return jsonify({'users': users})

@app.route('/api/users', methods=['POST'])
@require_api_key
def add_user():
    data = request.get_json()
    username = data.get('username')
    role = data.get('role', 'user')
    if not username:
        return jsonify({'error': 'Username required.'}), 400
    users = load_users()
    if any(u['username'] == username for u in users):
        return jsonify({'error': 'Username already exists.'}), 400
    api_key = secrets.token_hex(16)
    save_user(username, api_key, role)
    return jsonify({'username': username, 'api_key': api_key, 'role': role})

@app.route('/api/users/<username>', methods=['DELETE'])
@require_api_key
def remove_user(username):
    delete_user(username)
    return jsonify({'message': f'User {username} removed.'})


# Global error handler for JSON errors
@app.errorhandler(Exception)
def handle_exception(e):
    import traceback
    return jsonify({'error': str(e), 'trace': traceback.format_exc()}), 500
POLICY_CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'policy_config.json')

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'message': 'DevShield-AI backend running.'})

# Get current policy config
@app.route('/api/policy', methods=['GET'])
@require_api_key
def get_policy():
    try:
        with open(POLICY_CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except Exception as e:
        return jsonify({'error': f'Failed to load policy config: {e}'}), 500
    return jsonify({'policy': config})

# Update policy config
@app.route('/api/policy', methods=['POST'])
@require_api_key
def update_policy():
    new_config = request.get_json()
    if not isinstance(new_config, dict):
        return jsonify({'error': 'Invalid policy config format.'}), 400
    try:
        with open(POLICY_CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(new_config, f, indent=2)
    except Exception as e:
        return jsonify({'error': f'Failed to update policy config: {e}'}), 500
    return jsonify({'message': 'Policy config updated.'})

# Reset policy config to default
@app.route('/api/policy/reset', methods=['POST'])
@require_api_key
def reset_policy():
    default_config = {
        "block_types": ["Password", "Secret Key"],
        "warn_types": ["API Key", "Token"],
        "enforce_env": True
    }
    try:
        with open(POLICY_CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=2)
    except Exception as e:
        return jsonify({'error': f'Failed to reset policy config: {e}'}), 500
    return jsonify({'message': 'Policy config reset to default.'})


# Dashboard analytics endpoint
@app.route('/api/dashboard/summary', methods=['GET'])
@require_api_key
def dashboard_summary():
    conn = get_db()
    rows = conn.execute('SELECT response, request FROM analysis_log').fetchall()
    conn.close()
    total = len(rows)
    by_action = {}
    by_pattern = {}
    for row in rows:
        try:
            response = json.loads(row['response'])
            request = json.loads(row['request'])
        except Exception:
            continue
        action = response.get('action', 'unknown')
        pattern = request.get('pattern_type', 'unknown')
        by_action[action] = by_action.get(action, 0) + 1
        by_pattern[pattern] = by_pattern.get(pattern, 0) + 1
    return jsonify({
        'total_events': total,
        'by_action': by_action,
        'by_pattern': by_pattern
    })

# Event history endpoint
@app.route('/api/dashboard/events', methods=['GET'])
@require_api_key
def dashboard_events():
    conn = get_db()
    rows = conn.execute('SELECT timestamp, request, response FROM analysis_log ORDER BY id DESC LIMIT 100').fetchall()
    conn.close()
    events = []
    for row in rows:
        try:
            event = {
                'timestamp': row['timestamp'],
                'request': json.loads(row['request']),
                'response': json.loads(row['response'])
            }
            events.append(event)
        except Exception:
            continue
    return jsonify({'events': events})


@app.route('/api/analyze', methods=['POST'])
@require_api_key
@rate_limiter('analyze')
def analyze_secret():
    if not request.is_json:
        return jsonify({'error': 'Request must be JSON.'}), 400
    data = request.get_json()
    # Input validation
    required_fields = ['pattern_type', 'variable_name', 'filename', 'line']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    # 1. AI Risk Scoring
    ai_result = assess_risk(data)
    risk_score = ai_result.get('risk_score', 0)
    explanation = ai_result.get('explanation', '')
    # 2. Policy Check
    policy = check_policy(data.get('pattern_type', ''), {'variable': data.get('variable_name', '')})
    action = policy.get('action', ai_result.get('action', 'allow'))
    reason = policy.get('reason', '')
    # 3. Explanation (combine AI and policy)
    full_explanation = f"{explanation} Policy: {reason}"
    response = {
        'risk_score': risk_score,
        'action': action,
        'explanation': full_explanation
    }
    log_analysis(data, response)
    return jsonify(response)

if __name__ == '__main__':
    app.run(port=8000, debug=True)
