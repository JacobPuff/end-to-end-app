# -*- coding: utf-8 -*-

from sqlalchemy import (
    BIGINT,
    Boolean,
    Column,
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Time,
    Text,
    func)

from sqlalchemy.orm import relationship, Session
from .meta import Base

class User(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True)
    username = Column(String(32), nullable=False)
    password = Column(String(80), nullable=False)

    posts = relationship('Post', 
                         primaryjoin='Post.poster==User.user_id',
                         order_by='Post.post_id.desc()')