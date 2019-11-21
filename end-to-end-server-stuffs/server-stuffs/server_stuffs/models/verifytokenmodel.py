from sqlalchemy import (
    Column,
    Integer,
    TIMESTAMP,
    Text,
    String,
    func,
    ForeignKey
)

from .meta import Base


class VerifyTokenModel(Base):
    __tablename__ = 'verifytokens'
    verifytoken_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id', ondelete='CASCADE'))
    temp_email = Column(String(254), nullable=True, server_default=None)
    started = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp())
    token = Column(Text, nullable=False)
