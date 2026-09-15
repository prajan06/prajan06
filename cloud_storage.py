import os, json, tempfile
import boto3
from botocore.exceptions import BotoCoreError, ClientError

BUCKET = os.getenv("AWS_S3_BUCKET", "")
REGION = os.getenv("AWS_REGION", "ap-south-1")

def s3_client():
    # boto3 uses environment variables, AWS profile, or IAM role automatically.
    return boto3.client("s3", region_name=REGION)

def cloud_enabled():
    return bool(BUCKET)

def upload_encrypted_patient(patient_id, encrypted_data, encrypted_key):
    if not BUCKET:
        raise RuntimeError("AWS_S3_BUCKET is not configured.")
    body = json.dumps({
        "patient_id": patient_id,
        "encrypted_data": encrypted_data,
        "encrypted_key": encrypted_key
    }).encode()
    s3_client().put_object(
        Bucket=BUCKET,
        Key=f"patients/{patient_id}.json",
        Body=body,
        ServerSideEncryption="AES256",
        ContentType="application/json"
    )

def download_encrypted_patient(patient_id):
    if not BUCKET:
        raise RuntimeError("AWS_S3_BUCKET is not configured.")
    obj = s3_client().get_object(Bucket=BUCKET, Key=f"patients/{patient_id}.json")
    return json.loads(obj["Body"].read().decode())

def delete_encrypted_patient(patient_id):
    if BUCKET:
        s3_client().delete_object(Bucket=BUCKET, Key=f"patients/{patient_id}.json")
