from sqlalchemy import (
    Column,
    Integer,
    Text,
    ForeignKey
)

from .meta import Base


class TaskListModel(Base):
    __tablename__ = 'tasklists'
    list_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id', ondelete="CASCADE"), nullable=False)
    list_name = Column(Text, nullable=False)
