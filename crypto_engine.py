import os, json, base64
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

PRIVATE_KEY="private_key.pem"; PUBLIC_KEY="public_key.pem"

def ensure_rsa_keys():
    if not os.path.exists(PRIVATE_KEY):
        private = rsa.generate_private_key(public_exponent=65537,key_size=2048)
        with open(PRIVATE_KEY,"wb") as f: f.write(private.private_bytes(
            serialization.Encoding.PEM,serialization.PrivateFormat.PKCS8,serialization.NoEncryption()))
        with open(PUBLIC_KEY,"wb") as f: f.write(private.public_key().public_bytes(
            serialization.Encoding.PEM,serialization.PublicFormat.SubjectPublicKeyInfo))

def encrypt_patient(record):
    aes_key=os.urandom(32); nonce=os.urandom(12)
    data=json.dumps(record).encode()
    ct=AESGCM(aes_key).encrypt(nonce,data,None)
    with open(PUBLIC_KEY,"rb") as f: pub=serialization.load_pem_public_key(f.read())
    wrapped=pub.encrypt(aes_key,padding.OAEP(mgf=padding.MGF1(hashes.SHA256()),algorithm=hashes.SHA256(),label=None))
    return base64.b64encode(nonce+ct).decode(),base64.b64encode(wrapped).decode()

def decrypt_patient(encrypted_data, encrypted_key):
    with open(PRIVATE_KEY,"rb") as f: private=serialization.load_pem_private_key(f.read(),password=None)
    aes=private.decrypt(base64.b64decode(encrypted_key),padding.OAEP(mgf=padding.MGF1(hashes.SHA256()),algorithm=hashes.SHA256(),label=None))
    raw=base64.b64decode(encrypted_data); return json.loads(AESGCM(aes).decrypt(raw[:12],raw[12:],None).decode())
