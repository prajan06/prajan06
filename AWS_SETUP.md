# AWS S3 Setup

## 1. Create an S3 bucket
Create a private S3 bucket in AWS. Example region: `ap-south-1` (Mumbai).

## 2. Create an IAM user/role with only the required S3 permissions
For this demo, allow access to the chosen bucket for:
- s3:PutObject
- s3:GetObject
- s3:DeleteObject (optional)

Do not commit AWS keys to GitHub.

## 3. Configure AWS credentials on Windows
Recommended for a local demo:
```powershell
aws configure
```
Enter your AWS Access Key ID, Secret Access Key and region.

Or set environment variables for the session:
```powershell
$env:AWS_ACCESS_KEY_ID="YOUR_ACCESS_KEY"
$env:AWS_SECRET_ACCESS_KEY="YOUR_SECRET_KEY"
$env:AWS_REGION="ap-south-1"
$env:AWS_S3_BUCKET="YOUR_BUCKET_NAME"
```

You can also permanently configure `AWS_REGION` and `AWS_S3_BUCKET` through Windows Environment Variables.

## 4. Run
```powershell
python database.py
python app.py
```

When the bucket variable is configured, the dashboard shows **AWS S3 ON**.

### Security note
The application encrypts the patient JSON with AES-256-GCM before uploading. The S3 object contains ciphertext and the RSA-wrapped AES key, not plaintext patient information. S3 Server-Side Encryption (AES256) is also enabled as an additional storage layer.

This is an academic demo, not a production medical-record system.
