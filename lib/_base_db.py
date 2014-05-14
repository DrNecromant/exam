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

	# === # Main operations # === #

	def commit(self):
		self.session.commit()

	def rollback(self):
		self.session.rollback()

	def close(self):
		self.session.close()

	# === # File operations # === #

	def createFile(self, name, sha):
		self.session.add(File(name = name, sha = sha))

	def deleteFile(self, name):
		query = self.session.query(File).filter(File.name == name)
		query.delete(synchronize_session = False)

	def getFileNames(self):
		return map(lambda a: a.name, self.session.query(File).all())

	def updateFileSha(self, fname, sha):
		self.session.query(File).filter(File.name == fname).one().sha = sha

	def getFileSha(self, name):
		return self.session.query(File).filter(File.name == name).one().sha

	# === # Word operations # === #

	def createWord(self, fname, eng, rus, date):
		f = self.session.query(File).filter(File.name == fname).one()
		word = Word(eng = eng, rus = rus)
		f.words.append(word)
		word.history.append(History(date = date))

	def deleteWord(self, fname, eng, date):
		file_id = self.session.query(File).filter(File.name == fname).one().id
		query = self.session.query(Word).filter((Word.file == file_id) & (Word.eng == eng))
		word = query.one()
		word.history.append(History(date = date, passed = -1, failed = -1))
		query.delete(synchronize_session = False)

	def updateWord(self, fname, eng, rus):
		query = self.session.query(Word).join(File)
		query.filter((Word.eng == eng) & (File.name == fname)).one().rus = rus

	def getWordEntries(self, eng, rus, fname, output):
		query = self.session.query(Word.eng, Word.rus, File.name).join(File)
		if fname:
			query = query.filter(File.name == fname)
		if eng and eng != True:
			query = query.filter(Word.eng == eng)
		if rus and rus != True:
			query = query.filter(Word.rus == rus)
		entries = query.all()
		if not entries:
			return None
		entries_zip = zip(*entries)
		result_zip = list()
		if output & 1:
			result_zip.append(entries_zip[0])
		if output & 2:
			result_zip.append(entries_zip[1])
		if output & 4:
			result_zip.append(entries_zip[2])
		if len(result_zip) == 1:
			result = result_zip[0]
		else:
			result = zip(*result_zip)
		return result

	def getWordsLike(self, word):
		query = self.session.query(Word.eng, Word.rus, File.name).join(File)
		return query.filter(Word.eng.like("%" + word + "%")).all()

	def getWordsByStats(self, max_passed):
		query = self.session.query(Word.eng, Word.rus, File.name).join(File)
		if max_passed:
			query = query.filter(Word.passed <= max_passed)
		return query.order_by(Word.passed + Word.failed, Word.passed).all()

	# === # Stats operations  # === #

	def getMaxCounter(self, counter):
		return self.session.query(func.max(getattr(Word, counter))).scalar()

	def getHistoryByDate(self, date):
		stats = self.session.query(func.max(History.date), History.passed, History.failed)
		stats = stats.filter(History.date < date)
		stats = stats.group_by(History.word)
		stats = stats.having(History.passed > -1)
		return map(lambda s: s[1:], stats.all())

	def getMinDate(self):
		return self.session.query(func.date(func.min(History.date))).scalar()

	def getMaxDate(self):
		return self.session.query(func.date(func.max(History.date))).scalar()

	def updateCounter(self, eng, counter, date):
		word = self.session.query(Word).filter(Word.eng == eng).one()
		count = int(getattr(word, counter)) + 1
		setattr(word, counter, count)
		history = History(date = date, passed = word.passed, failed = word.failed)
		word.history.append(history)

	def getHistoryCountByDate(self, date_str):
		query = self.session.query(func.count(History.id)).filter(History.date.like(date_str + "%"))
		return query.filter((History.passed > 0) | (History.failed > 0)).scalar()

	# === # Lingvo operations # === #

	def getWordStats(self, eng):
		word = self.session.query(Word).filter(Word.eng == eng).one()
		return word.tr_num, word.ex_num, word.ph_num, word.updated

	def setWordStats(self, eng, tr_num, ex_num, ph_num, updated):
		word = self.session.query(Word).filter(Word.eng == eng).one()
		word.tr_num = tr_num
		word.ex_num = ex_num
		word.ph_num = ph_num
		word.updated = updated

	def createExamples(self, eng, examples):
		word = self.session.query(Word).filter(Word.eng == eng).one()
		for ex_eng, ex_rus in examples:
			example = self.session.query(Example).filter(Example.eng == ex_eng).first()
			if not example:
				example = Example(eng = ex_eng, rus = ex_rus)
				self.session.add(example)
				self.session.flush()
			word.examples.append(WordExample(word_id = word.id, example_id = example.id))

	def getExamples(self, eng):
		word = self.session.query(Word).filter(Word.eng == eng).one()
		example_ids = map(lambda x: x.example_id, word.examples)
		return self.session.query(Example.eng, Example.rus).filter(Example.id.in_(example_ids)).all()
