from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped
from sqlalchemy import String, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from app.db.database import engine


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))


class Memory(Base):
    __tablename__ = "memory"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    text: Mapped[dict] = mapped_column(JSONB, nullable=False)
