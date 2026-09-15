import hashlib
from datetime import datetime, timezone
from database import get_connection

def add_audit(username, action, details=""):
    con=get_connection()
    last=con.execute("SELECT current_hash FROM audit_logs ORDER BY id DESC LIMIT 1").fetchone()
    prev=last["current_hash"] if last else "GENESIS"
    ts=datetime.now(timezone.utc).isoformat()
    cur=hashlib.sha256(f"{prev}|{username}|{action}|{details}|{ts}".encode()).hexdigest()
    con.execute("INSERT INTO audit_logs(username,action,details,timestamp,previous_hash,current_hash) VALUES(?,?,?,?,?,?)",
                (username,action,details,ts,prev,cur)); con.commit(); con.close()

def verify_audit_chain():
    con=get_connection(); rows=con.execute("SELECT * FROM audit_logs ORDER BY id").fetchall(); con.close()
    prev="GENESIS"
    for r in rows:
        expected=hashlib.sha256(f"{prev}|{r['username']}|{r['action']}|{r['details']}|{r['timestamp']}".encode()).hexdigest()
        if r["previous_hash"]!=prev or r["current_hash"]!=expected: return False
        prev=expected
    return True
