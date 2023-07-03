from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table

from src.auth.models import User
from src.database import Base, metadata

post = Table(
    "post",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("title", String, nullable=False),
    Column("text", String, nullable=True),
    Column("views", Integer, default=0),
    Column("user_id", Integer, ForeignKey(User.id)),
)

user_post = Table(
    "user_post",
    metadata,
    Column("user_id", Integer, ForeignKey(User.id), primary_key=True),
    Column("post_id", Integer, ForeignKey(post.c.id), primary_key=True),
    Column("like", Boolean, nullable=False),
)


class Post(Base):
    __tablename__ = "post"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    text = Column(String, nullable=True)
    views = Column(Integer, default=0)
    user_id = Column(Integer, ForeignKey(User.id))


class UserPost(Base):
    __tablename__ = "user_post"
    user_id = Column(Integer, ForeignKey(User.id), primary_key=True)
    post_id = Column(Integer, ForeignKey(post.c.id), primary_key=True)
    like = Column(Boolean, nullable=False)
