import os

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Enum,
    TIMESTAMP,
    Boolean,
    ForeignKey,
    Date,
    func,
)
from sqlalchemy.sql import expression
from sqlalchemy.orm import sessionmaker, declarative_base, relationship

from src.platform.result import PlatformType

__all__ = ["Novel", "NovelInfo", "Episode", "session"]

engine = create_engine(os.environ.get("DB_URL"))

Base = declarative_base()


class NovelTagRef(Base):
    __tablename__ = "novel-tag-ref"

    novel_id = Column(Integer, ForeignKey("novel.id"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("novel-tag.id"), primary_key=True)


class Novel(Base):
    __tablename__ = "novel"
    id = Column(Integer, primary_key=True)

    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(
        TIMESTAMP,
        nullable=False,
        server_default=func.now(),
        onupdate=func.current_timestamp(),
    )
    title = Column(String, nullable=False)
    type = Column(Enum(PlatformType), nullable=False)
    thumbnail = Column(String)
    link = Column(String, nullable=False)
    author = Column(String, nullable=False)
    description = Column(String, nullable=False)
    is_end = Column(Boolean, server_default=expression.false(), default=True)
    is_plus = Column(Boolean, server_default=expression.false(), default=True)
    age_limit = Column(Integer, nullable=False)
    is_able = Column(Boolean, server_default=expression.false(), default=True)
    tags = relationship("Tag", secondary=NovelTagRef.__table__, back_populates="novels")


class Tag(Base):
    __tablename__ = "novel-tag"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    novels = relationship(
        "Novel", secondary=NovelTagRef.__table__, back_populates="tags"
    )


class NovelInfo(Base):
    __tablename__ = "novel-info"
    id = Column(Integer, primary_key=True)

    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())

    view = Column(Integer, nullable=False)
    good = Column(Integer, nullable=False)
    book = Column(Integer, nullable=False)

    novel_id = Column(Integer, ForeignKey("novel.id"), nullable=False)
    novel = relationship("Novel", foreign_keys=[novel_id])


class Episode(Base):
    __tablename__ = "novel-episode"
    id = Column(Integer, primary_key=True)

    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())

    idx = Column(Integer, nullable=False)
    title = Column(String, nullable=False)

    word_size = Column(String, nullable=False)

    view = Column(Integer, nullable=False)
    good = Column(Integer, nullable=False)
    comment = Column(Integer, nullable=False)

    date = Column(Date, nullable=False)

    novel_id = Column(Integer, ForeignKey("novel.id"), nullable=False)
    novel = relationship("Novel", foreign_keys=[novel_id])


Novel.__table__.create(bind=engine, checkfirst=True)
Tag.__table__.create(bind=engine, checkfirst=True)
NovelTagRef.__table__.create(bind=engine, checkfirst=True)
NovelInfo.__table__.create(bind=engine, checkfirst=True)
Episode.__table__.create(bind=engine, checkfirst=True)

Session = sessionmaker(bind=engine)
session = Session()
