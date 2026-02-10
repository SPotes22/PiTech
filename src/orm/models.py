import json
from typing import List, Optional

from .base import BaseORM


class FormModel(BaseORM):
    def __init__(self):
        super().__init__()

    def create_form(self, user_data: dict) -> int:
        query = """
            INSERT INTO forms (user_data, status)
            VALUES (?, ?)
        """
        return self.execute(query, (json.dumps(user_data), "pending"))

    def get_form(self, form_id: int) -> Optional[dict]:
        query = "SELECT * FROM forms WHERE id = ?"
        results = self.fetch(query, (form_id,))
        return results[0] if results else None

    def get_all_forms(self, archived: bool = False) -> List[dict]:
        query = "SELECT * FROM forms WHERE archived = ? ORDER BY created_at DESC"
        return self.fetch(query, (archived,))

    def archive_form(self, form_id: int) -> bool:
        query = "UPDATE forms SET archived = TRUE, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
        self.execute(query, (form_id,))
        return True

    def approve_form(self, form_id: int, approved_by: str) -> bool:
        query = """
            UPDATE forms
            SET status = 'approved',
                approved_by = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """
        self.execute(query, (approved_by, form_id))
        return True

    def decline_form(self, form_id: int, reason: str) -> bool:
        query = """
            UPDATE forms
            SET status = 'declined',
                declined_reason = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """
        self.execute(query, (reason, form_id))
        return True


class UserModel(BaseORM):
    def __init__(self):
        super().__init__()

    def create_user(
        self,
        username: str,
        role: str,
        hmac_secret: Optional[str] = None,
        api_key_hash: Optional[str] = None,
    ) -> int:
        query = """
            INSERT INTO users (username, role, hmac_secret, api_key_hash)
            VALUES (?, ?, ?, ?)
        """
        return self.execute(query, (username, role, hmac_secret, api_key_hash))

    def get_user_by_username(self, username: str) -> Optional[dict]:
        query = "SELECT * FROM users WHERE username = ? AND is_active = TRUE"
        results = self.fetch(query, (username,))
        return results[0] if results else None
