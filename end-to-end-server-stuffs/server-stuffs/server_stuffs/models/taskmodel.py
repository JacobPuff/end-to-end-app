from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    Text,
    ForeignKey
)

from .meta import Base


class TaskModel(Base):
    __tablename__ = 'tasks'
    task_id = Column(Integer, primary_key=True, autoincrement=True)
    list_id = Column(Integer, ForeignKey('tasklists.list_id', ondelete="CASCADE"), nullable=False)
    task_name = Column(Text, nullable=False)
    task_done = Column(Boolean, nullable=False, default=False)
