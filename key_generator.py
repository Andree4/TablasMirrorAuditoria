import os
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend


def generate_rsa_keys():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    public_key = private_key.public_key()

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    os.makedirs('keys', exist_ok=True)
    with open('keys/private_key.pem', 'wb') as f:
        f.write(private_pem)
    with open('keys/public_key.pem', 'wb') as f:
        f.write(public_pem)

    return private_key, public_key


def load_public_key():
    with open('keys/public_key.pem', 'rb') as f:
        public_pem = f.read()
    return serialization.load_pem_public_key(public_pem, backend=default_backend())


def load_private_key(pem_data):
    try:
        return serialization.load_pem_private_key(
            pem_data.encode('utf-8'),
            password=None,
            backend=default_backend()
        )
    except Exception:
        return None
