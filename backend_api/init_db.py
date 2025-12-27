# Database initialization script for DevShield-AI backend
import sqlite3

conn = sqlite3.connect('devshield.db')
c = conn.cursor()


# Users table (with email, password hash, no approval)
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    email TEXT UNIQUE,
    password_hash TEXT,
    api_key TEXT UNIQUE NOT NULL,
    role TEXT NOT NULL
)
''')

# Analysis log table
c.execute('''
CREATE TABLE IF NOT EXISTS analysis_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    request TEXT NOT NULL,
    response TEXT NOT NULL
)
''')

# Insert default admin user if not exists
c.execute('''
INSERT OR IGNORE INTO users (username, api_key, role) VALUES (?, ?, ?)''',
          ('admin', 'devshield-demo-key', 'admin'))

conn.commit()
conn.close()
print('Database initialized.')
