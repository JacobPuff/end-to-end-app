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

class Post(Base):
    __tablename__ = 'posts'
    post_id = Column(Integer, primary_key=True)
    parent = Column(Integer, ForeignKey('posts.post_id'), nullable=True)
    poster = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    subject = Column(String(256), nullable=False)
    body = Column(Text, nullable=False)

    user = relationship('User', foreign_keys=poster)
    parent_post = relationship('Post', foreign_keys=parent)