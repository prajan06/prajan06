# SecureVault Health
Encrypted patient record storage and access control mini project.

## Run on Windows
1. Extract the ZIP.
2. Open the folder in VS Code.
3. Open Terminal.
4. `py -3.14 -m venv venv`
5. `venv\Scripts\activate`
6. `pip install -r requirements.txt`
7. `python database.py`
8. `python app.py`
9. Open http://127.0.0.1:5000/

Demo accounts:
- doctor / doctor123
- admin / admin123
- auditor / auditor123


## AWS Cloud Mode
See `AWS_SETUP.md`. When `AWS_S3_BUCKET` is configured, encrypted patient records are uploaded to Amazon S3 and fetched from S3 before authorized decryption. If it is not configured, the application continues in local mode.
