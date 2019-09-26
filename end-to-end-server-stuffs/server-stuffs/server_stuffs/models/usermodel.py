from sqlalchemy import (
    Column,
    Integer,
    Text,
    String,
    Boolean
)

from .meta import Base


class UserModel(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    user_name = Column(Text, nullable=False, unique=True)
    user_email = Column(String(254), nullable=False)
    user_pass = Column(Text, nullable=False)
    verified = Column(Boolean, default=False, server_default="f", nullable=False)
