from style import *
from sqlalchemy import create_engine, ForeignKey, Column, Integer, String, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, backref
from sqlalchemy.schema import MetaData, ColumnDefault
from sqlalchemy.engine import Engine

metadata = MetaData()
Base = declarative_base(metadata = metadata)

class File(Base):
	__tablename__ = 'file'
	__table_args__ = {'sqlite_autoincrement': True}

	id = Column(Integer, primary_key = True)
	name = Column(String)
	sha = Column(String, server_default = "nosha")

class Word(Base):
	__tablename__ = 'word'
	__table_args__ = {'sqlite_autoincrement': True}

	id = Column(Integer, primary_key = True)
	eng = Column(String)
	rus = Column(String)
	file = Column(Integer, ForeignKey('file.id'))
	count = Column(String, default = 0)
	fail = Column(Integer, default = 0, quote = False)

	file_id = relationship("File", backref = 'words')

class DB():
	__metaclass__ = DecoMeta
	def __init__(self, dbpath):
		engine = create_engine('sqlite:///%s' % dbpath, echo = False)
		Base.metadata.create_all(engine) 
		Session = sessionmaker(bind = engine)
		self.session = Session()
		self.changes = self.getBlankChanges()

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
		return self.session.query(Word.eng, Word.rus, File.name).join(File).all()

	def updateCounter(self, eng, counter):
		word = self.session.query(Word).filter(Word.eng == eng).one()
		count = int(getattr(word, counter)) + 1
		setattr(word, counter, count)
		self.changes["update"].append("%s %s %s" % (eng, counter, count))

	def getSha(self, name):
		return self.session.query(File).filter(File.name == name).one().sha

	def updateSha(self, fname, sha):
		self.session.query(File).filter(File.name == fname).one().sha = sha
		self.changes["update"].append("%s | %s" % (fname, sha))

	def loadData(self, name):
		return self.session.query(Word.eng, Word.rus).join(File).filter(File.name == name).all()

	def deleteFile(self, fname):
		f = self.session.query(File).filter(File.name == fname)
		file_id = f.one().id
		self.session.query(Word).filter(Word.file == file_id).delete(synchronize_session = False)
		f.delete(synchronize_session = False)
		self.changes["delete"].append("%s | all words" % fname)

	def createFile(self, fname, sha, words):
		self.session.add(File(name = fname, sha = sha))
		for word in words:
			eng, rus = word
			self.createWord(fname, eng, rus)
		self.changes["create"].append("%s | %s" % (fname, sha))

	def deleteWord(self, fname, eng):
		file_id = self.session.query(File).filter(File.name == fname).one().id
		self.session.query(Word).filter((Word.id == file_id) & (Word.eng == eng)).delete(synchronize_session = False)
		self.changes["delete"].append("%s | %s" % (fname, eng))

	def createWord(self, fname, eng, rus):
		f = self.session.query(File).filter(File.name == fname).one()
		f.words.append(Word(eng = eng, rus = rus))
		self.changes["create"].append("%s | %s | %s" % (fname, eng, rus))

	def updateWord(self, fname, eng, rus1, rus2):
		self.session.query(Word).join(File).filter((Word.eng == eng) & (File.name == fname)).one().rus = rus2
		self.changes["update"].append("%s | %s | %s -> %s" % (fname, eng, rus1, rus2))

	def getStats(self):
		all_entries = self.session.query(Word.id, Word.eng, Word.count, Word.fail, File.name).join(File).all()
		result_table = [["word_id", "basedir", "filename", "single", "count", "fail"]]
		for entry in all_entries:
			basedir = entry.name.split("/")[1]
			filename = "/".join(entry.name.split("/")[2:])
			if " " in entry.eng:
				single = 1
			else:
				single = 0
			result_table.append([entry.id, basedir, filename, single, entry.count, entry.fail])
		return result_table
