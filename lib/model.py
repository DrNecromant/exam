from sqlalchemy import ForeignKey, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.schema import MetaData

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
	translations = Column(Integer)
	examples = Column(Integer)
	phrases = Column(Integer)
	date = Column(DateTime)

	lingvo = relationship("Lingvo")
	history = relationship("History")

class Lingvo(Base):
	__tablename__ = 'Lingvo'
	__table_args__ = {'sqlite_autoincrement': True}

	id = Column(Integer, primary_key = True)
	word = Column(Integer, ForeignKey('word.id'))
	eng = Column(String)
	rus = Column(String)

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
