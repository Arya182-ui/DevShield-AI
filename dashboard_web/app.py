from flask import Flask, render_template, jsonify, redirect, request
import sqlite3
import os

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(__file__), '../backend_api/devshield.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/users')
def users_page():
    return render_template('admin.html')

@app.route('/policy')
def policy_page():
    return render_template('admin.html')

# Proxy API endpoints for users and policy (reuse backend API)
import requests
BACKEND = 'http://localhost:8000'

@app.route('/api/users', methods=['GET'])
def api_users():
    r = requests.get(f'{BACKEND}/api/users', headers={'X-API-Key': 'devshield-demo-key'})
    return r.content, r.status_code, r.headers.items()

@app.route('/api/users/<username>', methods=['DELETE'])
def api_remove_user(username):
    r = requests.delete(f'{BACKEND}/api/users/{username}', headers={'X-API-Key': 'devshield-demo-key'})
    return r.content, r.status_code, r.headers.items()

@app.route('/api/policy', methods=['GET', 'POST'])
def api_policy():
    if request.method == 'GET':
        r = requests.get(f'{BACKEND}/api/policy', headers={'X-API-Key': 'devshield-demo-key'})
        return r.content, r.status_code, r.headers.items()
    else:
        r = requests.post(f'{BACKEND}/api/policy', headers={'X-API-Key': 'devshield-demo-key'}, json=request.get_json())
        return r.content, r.status_code, r.headers.items()
    
@app.route('/api/analytics')
def analytics():
    conn = get_db()
    rows = conn.execute('SELECT response FROM analysis_log').fetchall()
    conn.close()
    total = len(rows)
    by_action = {}
    for row in rows:
        try:
            response = eval(row['response']) if isinstance(row['response'], str) else row['response']
            action = response.get('action', 'unknown')
            by_action[action] = by_action.get(action, 0) + 1
        except Exception:
            continue
    return jsonify({'total_events': total, 'by_action': by_action})

@app.route('/api/history')
def history():
    conn = get_db()
    rows = conn.execute('SELECT timestamp, request, response FROM analysis_log ORDER BY id DESC LIMIT 100').fetchall()
    conn.close()
    events = []
    for row in rows:
        try:
            events.append({
                'timestamp': row['timestamp'],
                'request': row['request'],
                'response': row['response']
            })
        except Exception:
            continue
    return jsonify({'events': events})

if __name__ == '__main__':
    app.run(port=5050, debug=True)
