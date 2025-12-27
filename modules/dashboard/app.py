"""
app.py
------
Flask backend for DevShield AI Dashboard.
Provides API endpoints and serves the dashboard UI.
"""

from flask import Flask, render_template, jsonify, request
from datetime import datetime
from collections import Counter
import random

app = Flask(__name__)

# --- Demo/mock dataset ---
# Each entry: {id, timestamp, secret_type, risk_score, action, details}
MOCK_DATA = [
    {
        "id": 1,
        "timestamp": "2025-12-22T08:12:00",
        "secret_type": "API Key",
        "risk_score": 91,
        "action": "block",
        "details": "Blocked API key in src/app/config.py by user alice"
    },
    {
        "id": 2,
        "timestamp": "2025-12-22T08:23:00",
        "secret_type": "Token",
        "risk_score": 68,
        "action": "warn",
        "details": "Warned about token in frontend.js by user bob"
    },
    {
        "id": 3,
        "timestamp": "2025-12-22T08:35:00",
        "secret_type": "Password",
        "risk_score": 97,
        "action": "block",
        "details": "Blocked password in .env by user carol"
    },
    {
        "id": 4,
        "timestamp": "2025-12-22T09:01:00",
        "secret_type": "Secret Key",
        "risk_score": 82,
        "action": "block",
        "details": "Blocked secret key in backend/settings.py by user dave"
    },
    {
        "id": 5,
        "timestamp": "2025-12-22T09:15:00",
        "secret_type": "API Key",
        "risk_score": 74,
        "action": "warn",
        "details": "Warned about API key in mobile/app.js by user eve"
    },
    {
        "id": 6,
        "timestamp": "2025-12-22T09:30:00",
        "secret_type": "Password",
        "risk_score": 88,
        "action": "block",
        "details": "Blocked password in docker-compose.yml by user frank"
    },
    {
        "id": 7,
        "timestamp": "2025-12-22T09:45:00",
        "secret_type": "Token",
        "risk_score": 62,
        "action": "warn",
        "details": "Warned about token in api/routes.py by user grace"
    },
    {
        "id": 8,
        "timestamp": "2025-12-22T10:00:00",
        "secret_type": "Secret Key",
        "risk_score": 79,
        "action": "block",
        "details": "Blocked secret key in infra/terraform.tfvars by user heidi"
    },
]

# --- Helper functions ---
def get_next_id():
    return max([d['id'] for d in MOCK_DATA], default=0) + 1

# --- API Endpoints ---

@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    """Return dashboard metrics: total blocked, type breakdown, risk scores, timeline."""
    total_blocked = sum(1 for d in MOCK_DATA if d['action'] == 'block')
    type_breakdown = dict(Counter(d['secret_type'] for d in MOCK_DATA))
    risk_scores = [d['risk_score'] for d in MOCK_DATA]
    timeline = sorted(MOCK_DATA, key=lambda d: d['timestamp'], reverse=True)
    return jsonify({
        "total_blocked": total_blocked,
        "type_breakdown": type_breakdown,
        "risk_scores": risk_scores,
        "timeline": timeline
    })

@app.route('/api/events', methods=['GET'])
def get_events():
    """Return all secret detection events (activity feed)."""
    return jsonify(MOCK_DATA)

@app.route('/api/events', methods=['POST'])
def add_event():
    """Add a new secret detection event (integration endpoint)."""
    data = request.json
    event = {
        "id": get_next_id(),
        "timestamp": data.get("timestamp", datetime.utcnow().isoformat()),
        "secret_type": data.get("secret_type", "Unknown"),
        "risk_score": int(data.get("risk_score", random.randint(50, 100))),
        "action": data.get("action", "block"),
        "details": data.get("details", "")
    }
    MOCK_DATA.append(event)
    return jsonify(event), 201

@app.route('/api/events/<int:event_id>', methods=['PUT'])
def update_event(event_id):
    """Update an event (demo CRUD)."""
    data = request.json
    for event in MOCK_DATA:
        if event['id'] == event_id:
            event.update(data)
            return jsonify(event)
    return jsonify({"error": "Event not found"}), 404

@app.route('/api/events/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    """Delete an event (demo CRUD)."""
    global MOCK_DATA
    MOCK_DATA = [e for e in MOCK_DATA if e['id'] != event_id]
    return '', 204

# --- Dashboard UI ---
@app.route('/')
def dashboard():
    """Serve the dashboard UI."""
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
