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
	tr_num = Column(Integer)
	ex_num = Column(Integer)
	ph_num = Column(Integer)
	updated = Column(DateTime)

	history = relationship("History")
	examples = relationship("WordExample")

class Example(Base):
	__tablename__ = 'example'
	__table_args__ = {'sqlite_autoincrement': True}

	id = Column(Integer, primary_key = True)
	eng = Column(String)
	rus = Column(String)

	words = relationship("WordExample")

class WordExample(Base):
	__tablename__ = 'wordexample'
	__table_args__ = {'sqlite_autoincrement': True}

	id = Column(Integer, primary_key = True)
	word_id = Column(Integer, ForeignKey('word.id'))
	example_id = Column(Integer, ForeignKey('example.id'))

class History(Base):
	__tablename__ = 'history'
	__table_args__ = {'sqlite_autoincrement': True}

	id = Column(Integer, primary_key = True)
	date = Column(DateTime)
	word = Column(Integer, ForeignKey('word.id'))
	passed = Column(Integer, default = 0)
	failed = Column(Integer, default = 0)
