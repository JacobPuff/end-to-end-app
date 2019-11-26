from sqlalchemy import (
    Column,
    Integer,
    String
)

from .meta import Base


class EmailBlacklistModel(Base):
    __tablename__ = 'emailblacklist'
    email_id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(254), nullable=False)
