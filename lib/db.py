from style import *
from sqlalchemy import create_engine, ForeignKey, Column, Integer, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, backref
from sqlalchemy.schema import MetaData, ColumnDefault
from sqlalchemy.engine import Engine
from datetime import datetime

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

class DB():
	__metaclass__ = DecoMeta
	def __init__(self, dbpath):
		engine = create_engine('sqlite:///%s' % dbpath, echo = False)
		Base.metadata.create_all(engine) 
		Session = sessionmaker(bind = engine)
		self.session = Session()
		self.changes = self.getBlankChanges()
		self.now = None

	def getDateNow(self):
		if not self.now:
			self.now = datetime.now().replace(microsecond = 0)
		return self.now

	def getErrors(self):
		errors = dict()
		duplicates = self.session.query(Word).group_by(Word.eng).having(func.count(Word.rus) > 1).all()
		if duplicates:
			errors["duplicates"] = map(lambda a: a.eng, duplicates)
		spaces = self.session.query(Word).filter(Word.eng.like(" %") | Word.eng.like("% ") | Word.eng.like("%  %")).all()
		if spaces:
			errors["spaces"] = map(lambda a: a.eng, spaces)
		articles = self.session.query(Word).filter(Word.eng.like("a %") | Word.eng.like("the %")).all()
		if articles:
			errors["articles"] = map(lambda a: a.eng, articles)
		engs = self.session.query(Word.eng).all()
		rus_letters = [s[0] for s in engs if not all(ord(c) < 128 for c in s[0])]
		if rus_letters:
			errors["rus_letters"] = rus_letters
		signs = [s[0] for s in engs if "?" in s[0] or "!" in s[0] or "." in s[0] or "," in s[0] or "(" in s[0] or ")" in s[0]]
		if signs:
			errors["unused_signs"] = signs
		return errors

	def getChanges(self):
		return dict(self.changes)

	def getBlankChanges(self):
		return {"create": list(), "update": list(), "delete": list()}

	def quit(self):
		self.session.close()

	def commit(self, fake = False):
		if fake:
			print "Cannot apply database changes - fake mode"
			self.session.rollback()
		else:
			print "Apply database changes"
			self.session.commit()
		self.changes = self.getBlankChanges()

	def getAllFiles(self):
		return map(lambda a: a.name, self.session.query(File).all())

	def findWords(self, word):
		return self.session.query(Word.eng, Word.rus, File.name).join(File).filter(Word.eng.like("%" + word + "%")).all()

	def getWords(self, word):
		return self.session.query(Word.eng, Word.rus, File.name).join(File).filter(Word.eng == word).all()

	def getAllWords(self):
		return self.session.query(Word.eng, Word.rus, File.name).join(File).order_by((1000 * Word.failed) / (Word.failed + Word.passed)).all()

	def updateCounter(self, eng, counter):
		word = self.session.query(Word).filter(Word.eng == eng).one()
		history = History(date = self.getDateNow())
		count = int(getattr(word, counter)) + 1
		setattr(word, counter, count)
		setattr(history, counter, count)
		word.history.append(history)
		self.changes["update"].append("%s %s %s" % (eng, counter, count))

	def getSha(self, name):
		return self.session.query(File).filter(File.name == name).one().sha

	def updateSha(self, fname, sha):
		self.session.query(File).filter(File.name == fname).one().sha = sha
		self.changes["update"].append("%s | %s" % (fname, sha))

	def loadData(self, name):
		return self.session.query(Word.eng, Word.rus).join(File).filter(File.name == name).all()

	def deleteFile(self, fname):
		file_query = self.session.query(File).filter(File.name == fname)
		for word in file_query.one().words:
			self.deleteWord(fname, word.eng)
		file_query.delete(synchronize_session = False)
		self.changes["delete"].append("%s | all words" % fname)

	def deleteWord(self, fname, eng):
		file_id = self.session.query(File).filter(File.name == fname).one().id
		word_query = self.session.query(Word).filter((Word.file == file_id) & (Word.eng == eng))
		word_query.one().history.append(History(date = self.getDateNow(), passed = -1, failed = -1))
		word_query.delete(synchronize_session = False)
		self.changes["delete"].append("%s | %s" % (fname, eng))

	def createFile(self, fname, sha, words):
		self.session.add(File(name = fname, sha = sha))
		for word in words:
			eng, rus = word
			self.createWord(fname, eng, rus)
		self.changes["create"].append("%s | %s" % (fname, sha))

	def createWord(self, fname, eng, rus):
		f = self.session.query(File).filter(File.name == fname).one()
		word = Word(eng = eng, rus = rus)
		word.history.append(History(date = self.getDateNow()))
		f.words.append(word)
		self.changes["create"].append("%s | %s | %s" % (fname, eng, rus))

	def updateWord(self, fname, eng, rus1, rus2):
		self.session.query(Word).join(File).filter((Word.eng == eng) & (File.name == fname)).one().rus = rus2
		self.changes["update"].append("%s | %s | %s -> %s" % (fname, eng, rus1, rus2))

	def getStats(self):
		entries = self.session.query(Word.id, Word.eng, Word.passed, Word.failed, File.name).join(File).all()
		result_table = [["word_id", "basedir", "filename", "single", "passed", "failed"]]
		for entry in entries:
			basedir = entry.name.split("/")[1]
			filename = "/".join(entry.name.split("/")[2:])
			if " " in entry.eng:
				single = 1
			else:
				single = 0
			result_table.append([entry.id, basedir, filename, single, entry.passed, entry.failed])
		return result_table
