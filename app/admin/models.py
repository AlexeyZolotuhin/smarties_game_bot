from dataclasses import dataclass
from hashlib import sha256
from typing import Optional

from app.store.database.sqlalchemy_base import db
from sqlalchemy import (
    Column,
    Integer,
    VARCHAR,
)


@dataclass
class Admin:
    id: int
    login: str
    password: Optional[str] = None

    def is_password_valid(self, password: str):
        return self.password == sha256(password.encode()).hexdigest()

    @classmethod
    def from_session(cls, session: Optional[dict]) -> Optional["Admin"]:
        return cls(id=session["admin"]["id"], login=session["admin"]["login"])


class AdminModel(db):
    __tablename__ = "admins"
    id = Column(Integer, primary_key=True)
    login = Column(VARCHAR(50), nullable=False, unique=True)
    password = Column(VARCHAR(200), nullable=False)

    def __repr__(self):
        return f"<Admin(id='{self.id}', email='{self.email}')>"

    def set_attr(self, login: str, password: str) -> None:
        setattr(self, "login", login)
        setattr(self, "password", sha256(password.encode()).hexdigest())
