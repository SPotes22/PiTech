import base64
import hashlib
import os


class ParanoidVault:
    def __init__(self, vault_path: str):
        self.vault_path = vault_path
        os.makedirs(vault_path, exist_ok=True)

    def hash_with_salt(self, data: str) -> str:
        salt = os.urandom(32)
        hash_value = data.encode()
        for _ in range(10000):
            hash_value = hashlib.sha512(hash_value + salt).digest()
        combined = salt + hash_value
        return base64.b64encode(combined).decode()

    def verify_hash(self, data: str, stored_hash: str) -> bool:
        try:
            decoded = base64.b64decode(stored_hash)
            salt = decoded[:32]
            stored_digest = decoded[32:]
            hash_value = data.encode()
            for _ in range(10000):
                hash_value = hashlib.sha512(hash_value + salt).digest()
            return hash_value == stored_digest
        except Exception:
            return False
