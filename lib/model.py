from sqlalchemy import ForeignKey, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.schema import MetaData

__all__ = ['File', 'Word', 'History', 'DictEng', 'Base']

metadata = MetaData()
Base = declarative_base(metadata = metadata)

class File(Base):
	__tablename__ = 'file'
	__table_args__ = {'sqlite_autoincrement': True}

	id = Column(Integer, primary_key = True)
	name = Column(String)
	sha = Column(String, default = "NOSHA")

	words = relationship("Word")

class Word(Base):
	__tablename__ = 'word'
	__table_args__ = {'sqlite_autoincrement': True}

	id = Column(Integer, primary_key = True)
	eng = Column(String)
	rus = Column(String)
	file = Column(Integer, ForeignKey('file.id'))
	passed = Column(Integer, default = 0)
	failed = Column(Integer, default = 0)

	history = relationship("History")

class History(Base):
	__tablename__ = 'history'
	__table_args__ = {'sqlite_autoincrement': True}

	id = Column(Integer, primary_key = True)
	date = Column(DateTime)
	word = Column(Integer, ForeignKey('word.id'))
	passed = Column(Integer, default = 0)
	failed = Column(Integer, default = 0)

class DictEng(Base):
	__tablename__ = 'dicteng'
	__table_args__ = {'sqlite_autoincrement': True}

	id = Column(Integer, primary_key = True)
	eng = Column(String)
