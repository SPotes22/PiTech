import base64
import hashlib
import hmac
import time


class HMACAuth:
    def __init__(self, secret: str):
        self.secret = secret.encode()

    def generate_signature(self, message: str) -> str:
        h = hmac.new(self.secret, message.encode(), hashlib.sha256)
        return base64.b64encode(h.digest()).decode()

    def verify_signature(self, message: str, signature: str) -> bool:
        expected = self.generate_signature(message)
        return hmac.compare_digest(expected, signature)

    def generate_timestamped_token(self, username: str) -> dict:
        timestamp = str(int(time.time()))
        message = f"{username}:{timestamp}"
        signature = self.generate_signature(message)
        return {"username": username, "timestamp": timestamp, "signature": signature}
