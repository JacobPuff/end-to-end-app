from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
)

from .meta import Base


class TaskListModel(Base):
    __tablename__ = 'tasklists'
    list_id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    list_name = Column(Text)
