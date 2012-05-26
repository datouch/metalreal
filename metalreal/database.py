from sqlalchemy import create_engine, Table, Column, MetaData, ForeignKey, and_
from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import Sequence
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import \
    ARRAY, BIGINT, BIT, BOOLEAN, BYTEA, CHAR, CIDR, DATE, \
    DOUBLE_PRECISION, ENUM, FLOAT, INET, INTEGER, INTERVAL, \
    MACADDR, NUMERIC, REAL, SMALLINT, TEXT, TIME, TIMESTAMP, \
    UUID, VARCHAR

#:Database Preparation
engine = create_engine(
          "postgresql+psycopg2://tester:tester@localhost:5432/metalreal_dev",
          client_encoding='utf8',
          echo=True)

Base = declarative_base()

RequiredChapters = Table('required_chapters', Base.metadata,
    Column('chapter_id', None, ForeignKey('chapters.chapter_id',
                                          onupdate='CASCADE',
                                          ondelete='CASCADE'), 
                                          primary_key=True),
    Column('required_id', None, ForeignKey('chapters.chapter_id', 
                                          onupdate='CASCADE',
                                          ondelete='CASCADE'),
                                          primary_key=True)
  )

class Chapter(Base):
  # Table structure declaration
  __tablename__ = 'chapters'
  chapter_id = Column(VARCHAR(10), primary_key=True)
  title = Column(VARCHAR(120), nullable=False)
  content = Column(TEXT, nullable=False)
  updated_at = Column(TIMESTAMP, default='NOW', onupdate='NOW')
  # Required chapters association
  # and Chapter can get chapters that require them
  # using requiring_chapters
  required_chapters = relationship("Chapter",
                                   secondary=RequiredChapters,
                                   primaryjoin=chapter_id==RequiredChapters.c.chapter_id,
                                   secondaryjoin=chapter_id==RequiredChapters.c.required_id,
                                   backref="requiring_chapters")
  questions = relationship("Question",
                           backref="chapter")

  def __init__(self, chapter_id, title, content):
    self.chapter_id = chapter_id
    self.title = title
    self.content = content

class Question(Base):
  __tablename__ = 'question'
  id = Column(INTEGER, Sequence('question_seq'), primary_key=True)
  question = Column(TEXT, nullable=False)
  answer = Column(TEXT, nullable=False)
  type = Column(INTEGER)
  hint = Column(TEXT)
  chapter_id = Column(None, ForeignKey('chapters.chapter_id',
                                       onupdate='CASCADE',
                                       ondelete='CASCADE'))

  def __init__(self, question, answer, type, hint):
    self.question = question
    self.answer = answer
    self.type = type
    self.hint = hint

Base.metadata.create_all(engine)