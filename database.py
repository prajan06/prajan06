import sqlite3, os, hashlib, base64
from datetime import datetime, timezone

DB = "securevault.db"

def get_connection():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c

def password_hash(password, salt=None):
    salt = salt or os.urandom(16)
    key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 310000, 32)
    return base64.b64encode(salt + key).decode()

def verify_password(password, stored):
    raw = base64.b64decode(stored)
    salt, old = raw[:16], raw[16:]
    new = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 310000, 32)
    return __import__("hmac").compare_digest(new, old)

def initialize_database():
    con = get_connection()
    con.executescript("""
    CREATE TABLE IF NOT EXISTS users(
      id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL,
      password_hash TEXT NOT NULL, role TEXT NOT NULL,
      created_at TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS patients(
      id INTEGER PRIMARY KEY AUTOINCREMENT, patient_id TEXT UNIQUE NOT NULL,
      encrypted_data TEXT NOT NULL, encrypted_key TEXT NOT NULL,
      created_by TEXT NOT NULL, created_at TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS audit_logs(
      id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, action TEXT,
      details TEXT, timestamp TEXT, previous_hash TEXT, current_hash TEXT);
    """)
    con.commit(); con.close()

def create_default_users():
    con = get_connection()
    users = [("doctor","doctor123","Doctor"),("admin","admin123","Admin"),("auditor","auditor123","Auditor")]
    for u,p,r in users:
        if not con.execute("SELECT 1 FROM users WHERE username=?", (u,)).fetchone():
            con.execute("INSERT INTO users(username,password_hash,role,created_at) VALUES(?,?,?,?)",
                        (u,password_hash(p),r,datetime.now(timezone.utc).isoformat()))
    con.commit(); con.close()

if __name__ == "__main__":
    initialize_database(); create_default_users()
    print("Database initialized. Demo users: doctor, admin, auditor")
