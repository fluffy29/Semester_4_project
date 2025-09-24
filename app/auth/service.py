from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Optional
import uuid
from passlib.context import CryptContext


@dataclass
class User:
    id: str
    email: str
    password_hash: str
    role: str


class UserService:
    def __init__(self, pwd_context: CryptContext):
        self._pwd = pwd_context
        self._users: Dict[str, User] = {}
        self.create_user("student@example.com", "password", role="student")
        self.create_user("admin@example.com", "password", role="admin")

    def create_user(self, email: str, password: str, role: str = "student") -> User:
        existing = self.get_user_by_email(email)
        if existing:
            return existing
        user = User(id=str(uuid.uuid4()), email=email, password_hash=self._pwd.hash(password), role=role)
        self._users[user.id] = user
        return user

    def get_user_by_email(self, email: str) -> Optional[User]:
        return next((u for u in self._users.values() if u.email == email), None)

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        return self._users.get(user_id)

    def verify_password(self, plain: str, password_hash: str) -> bool:
        return self._pwd.verify(plain, password_hash)
