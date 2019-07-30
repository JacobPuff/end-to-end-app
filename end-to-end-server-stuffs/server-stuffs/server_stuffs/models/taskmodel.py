from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
    ForeignKey
)

from .meta import Base


class TaskModel(Base):
    __tablename__ = 'tasks'
    task_id = Column(Integer, primary_key=True)
    list_id = Column(Integer, ForeignKey('tasklists.list_id', ondelete="CASCADE"))
    user_id = Column(Integer)
    task_name = Column(Text)
