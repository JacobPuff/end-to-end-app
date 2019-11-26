from sqlalchemy import (
    Column,
    Integer,
    Text,
    String,
    Boolean,
    TIMESTAMP,
    func
)

from .meta import Base


class UserModel(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    user_name = Column(Text, nullable=False, unique=True)
    user_email = Column(String(254), nullable=False, unique=True)
    user_pass = Column(Text, nullable=False)
    started = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp())
    verified = Column(Boolean, default=False, server_default="f", nullable=False)
