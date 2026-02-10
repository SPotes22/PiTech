import secrets

from .vault_integration import ParanoidVault


class APIKeyAuth:
    def __init__(self, vault_path: str = "./vault"):
        self.vault = ParanoidVault(vault_path)

    def generate_api_key(self) -> str:
        return secrets.token_urlsafe(32)

    def hash_api_key(self, api_key: str) -> str:
        return self.vault.hash_with_salt(api_key)

    def verify_api_key(self, api_key: str, stored_hash: str) -> bool:
        return self.vault.verify_hash(api_key, stored_hash)
