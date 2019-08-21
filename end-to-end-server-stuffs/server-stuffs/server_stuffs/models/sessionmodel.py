from sqlalchemy import (
    Column,
    Integer,
    TIMESTAMP,
    Text,
    func,
    ForeignKey
)

from .meta import Base


class SessionModel(Base):
    __tablename__ = 'sessions'
    session_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id', ondelete='CASCADE'))
    started = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp())
    last_active = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp())
    token = Column(Text, nullable=False)
