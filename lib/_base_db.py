from style import *
from model import *
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker

class _base_DB():
	__metaclass__ = DecoMeta

	def __init__(self, dbpath):
		engine = create_engine('sqlite:///%s' % dbpath, echo = False)
		Base.metadata.create_all(engine) 
		Session = sessionmaker(bind = engine)
		self.session = Session()

	def getAllFiles(self):
		return map(lambda a: a.name, self.session.query(File).all())

	def findWords(self, word):
		return self.session.query(Word.eng, Word.rus, File.name).join(File).filter(Word.eng.like("%" + word + "%")).all()

	def getWords(self, word):
		return self.session.query(Word.eng, Word.rus, File.name).join(File).filter(Word.eng == word).all()

	def getAllWords(self):
		return self.session.query(Word.eng, Word.rus, File.name).join(File).\
		filter(Word.passed <= 5).order_by(Word.passed + Word.failed, Word.passed).all()

	def getMaxCounter(self, counter):
		return self.session.query(func.max(getattr(Word, counter))).scalar()

	def getSha(self, name):
		return self.session.query(File).filter(File.name == name).one().sha

	def loadData(self, name):
		return self.session.query(Word.eng, Word.rus).join(File).filter(File.name == name).all()

	def _getRawDataByDate(self, date):
		stats = self.session.query(func.max(History.date), History.passed, History.failed)
		stats = stats.filter(History.date < date)
		stats = stats.group_by(History.word)
		stats = stats.having(History.passed > -1)
		return map(lambda s: s[1:], stats.all())

	def getEngWords(self):
		query = self.session.query(Word)
		return map(lambda w: w.eng, query.all())

	def _getDates(self):
		return self.session.query(func.date(func.min(History.date)), func.date(func.max(History.date))).one()

	def _updateWord(self, fname, eng, rus):
		self.session.query(Word).join(File).filter((Word.eng == eng) & (File.name == fname)).one().rus = rus

	def createWordWithDate(self, fname, eng, rus, date):
		f = self.session.query(File).filter(File.name == fname).one()
		word = Word(eng = eng, rus = rus)
		f.words.append(word)
		word.history.append(History(date = date))

	def createFileWithSha(self, fname, sha):
		self.session.add(File(name = fname, sha = sha))

	def deleteWordFromFile(self, fname, eng, d):
		file_id = self.session.query(File).filter(File.name == fname).one().id
		word_query = self.session.query(Word).filter((Word.file == file_id) & (Word.eng == eng))
		word = word_query.one()
		word.history.append(History(date = d, passed = -1, failed = -1))
		word_query.delete(synchronize_session = False)

	def deleteFileByName(self, fname):
		self.session.query(File).filter(File.name == fname).delete(synchronize_session = False)

	def getWordsByFile(self, fname):
		query = self.session.query(Word).join(File).filter(File.name == fname)
		return query.all()

	def updateShaByFile(self, fname, sha):
		self.session.query(File).filter(File.name == fname).one().sha = sha

	def _updateCounter(self, eng, counter, d):
		word = self.session.query(Word).filter(Word.eng == eng).one()
		count = int(getattr(word, counter)) + 1
		setattr(word, counter, count)
		history = History(date = d, passed = word.passed, failed = word.failed)
		word.history.append(history)

	def _commit(self):
		self.session.commit()

	def _rollback(self):
		self.session.rollback()

	def quit(self):
		self.session.close()
