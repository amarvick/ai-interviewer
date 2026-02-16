import hashlib
import hmac
import os

def hash_password(password: str) -> str:
    salt = os.urandom(16)
    derived_key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
    return f"{salt.hex()}${derived_key.hex()}"

def verify_password(plain_password: str, stored_password_hash: str) -> bool:
    try:
        salt_hex, hash_hex = stored_password_hash.split("$", 1)
        salt = bytes.fromhex(salt_hex)
        expected_hash = bytes.fromhex(hash_hex)
    except ValueError:
        return False
    derived_key = hashlib.pbkdf2_hmac("sha256", plain_password.encode("utf-8"), salt, 100_000)
    return hmac.compare_digest(derived_key, expected_hash)
