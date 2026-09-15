from flask import Flask, render_template, request, redirect, url_for, session, flash
from database import get_connection, initialize_database, create_default_users, verify_password
from crypto_engine import ensure_rsa_keys, encrypt_patient, decrypt_patient
from audit import add_audit, verify_audit_chain
from cloud_storage import upload_encrypted_patient, download_encrypted_patient, cloud_enabled

app=Flask(__name__)
app.secret_key="securevault-demo-secret"
initialize_database(); create_default_users(); ensure_rsa_keys()

def login_required(f):
    from functools import wraps
    @wraps(f)
    def w(*a,**k):
        if "username" not in session: return redirect(url_for("login"))
        return f(*a,**k)
    return w

def role_required(*roles):
    def deco(f):
        from functools import wraps
        @wraps(f)
        def w(*a,**k):
            if session.get("role") not in roles:
                flash("Access denied for your role.","danger"); return redirect(url_for("dashboard"))
            return f(*a,**k)
        return w
    return deco

@app.route("/",methods=["GET","POST"])
def login():
    if request.method=="POST":
        u=request.form["username"].strip(); p=request.form["password"]
        con=get_connection(); row=con.execute("SELECT * FROM users WHERE username=?",(u,)).fetchone(); con.close()
        if row and verify_password(p,row["password_hash"]):
            session.update(username=u,role=row["role"]); add_audit(u,"LOGIN_SUCCESS","Password verified"); return redirect(url_for("dashboard"))
        flash("Invalid username or password.","danger")
    return render_template("login.html")

@app.route("/logout")
def logout():
    u=session.get("username")
    if u: add_audit(u,"LOGOUT")
    session.clear(); return redirect(url_for("login"))

@app.route("/dashboard")
@login_required
def dashboard():
    con=get_connection()
    patients=con.execute("SELECT COUNT(*) c FROM patients").fetchone()["c"]
    logs=con.execute("SELECT COUNT(*) c FROM audit_logs").fetchone()["c"]
    con.close()
    return render_template("dashboard.html",patients=patients,logs=logs,chain=verify_audit_chain(),cloud=cloud_enabled())

@app.route("/add-patient",methods=["GET","POST"])
@login_required
@role_required("Doctor","Admin")
def add_patient():
    if request.method=="POST":
        rec={k:request.form[k] for k in ["patient_id","name","age","blood_group","diagnosis","treatment"]}
        enc,key=encrypt_patient(rec)
        try:
            # Store encrypted payload locally and in S3. No plaintext is sent to S3.
            if cloud_enabled():
                upload_encrypted_patient(rec["patient_id"],enc,key)
            con=get_connection()
            con.execute("INSERT INTO patients(patient_id,encrypted_data,encrypted_key,created_by,created_at) VALUES(?,?,?,?,datetime('now'))",
                        (rec["patient_id"],enc,key,session["username"]))
            con.commit(); con.close()
            add_audit(session["username"],"PATIENT_ENCRYPTED",
                      rec["patient_id"] + (" | AWS S3" if cloud_enabled() else " | Local"))
            flash("Patient encrypted and stored " + ("locally + in AWS S3." if cloud_enabled() else "locally."),"success")
            return redirect(url_for("patients"))
        except Exception as e:
            flash("Storage failed: " + str(e),"danger")
    return render_template("add_patient.html")

@app.route("/patients")
@login_required
def patients():
    con=get_connection(); rows=con.execute("SELECT patient_id,created_by,created_at FROM patients ORDER BY id DESC").fetchall(); con.close()
    return render_template("patients.html",patients=rows)

@app.route("/patient/<pid>")
@login_required
@role_required("Doctor","Admin")
def view_patient(pid):
    con=get_connection(); row=con.execute("SELECT * FROM patients WHERE patient_id=?",(pid,)).fetchone(); con.close()
    if not row:
        flash("Patient not found.","danger"); return redirect(url_for("patients"))
    try:
        # Prefer encrypted object from S3 when cloud is enabled.
        if cloud_enabled():
            obj=download_encrypted_patient(pid)
            data=decrypt_patient(obj["encrypted_data"],obj["encrypted_key"])
            source="AWS S3"
        else:
            data=decrypt_patient(row["encrypted_data"],row["encrypted_key"])
            source="Local SQLite"
        add_audit(session["username"],"PATIENT_DECRYPTED",pid+" | "+source)
        return render_template("view_patient.html",patient=data)
    except Exception as e:
        add_audit(session["username"],"DECRYPT_FAILED",pid)
        flash("Decryption failed: "+str(e),"danger"); return redirect(url_for("patients"))

@app.route("/audit")
@login_required
@role_required("Admin","Auditor")
def audit():
    con=get_connection(); rows=con.execute("SELECT * FROM audit_logs ORDER BY id DESC").fetchall(); con.close()
    return render_template("audit.html",logs=rows)

@app.route("/security-check")
@login_required
def security():
    return render_template("security.html",cloud=cloud_enabled())

if __name__=="__main__":
    app.run(debug=True)
