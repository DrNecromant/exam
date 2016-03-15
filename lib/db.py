from style import *
from model import *
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from helpers import getCurrentDateTime

class DB():
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

	def createWord(self, fname, eng, rus):
		f = self.session.query(File).filter(File.name == fname).one()
		word = Word(eng = eng, rus = rus)
		f.words.append(word)
		word.history.append(History(date = getCurrentDateTime()))

	def deleteWord(self, fname, eng):
		file_id = self.session.query(File).filter(File.name == fname).one().id
		word_query = self.session.query(Word).filter((Word.file == file_id) & (Word.eng == eng))
		word = word_query.one()
		word.history.append(History(date = getCurrentDateTime(), passed = -1, failed = -1))
		example_query = self.session.query(WordExample).filter(WordExample.word_id == word.id)
		example_query.delete(synchronize_session = False)
		word_query.delete(synchronize_session = False)

	def updateWord(self, fname, eng, rus):
		query = self.session.query(Word).join(File)
		query.filter((Word.eng == eng) & (File.name == fname)).one().rus = rus

	def getWords(self, eng = None, rus = None, fname = None, output = 7, updated_before = None, eng_pattern = None, max_passed = None, rate = None):
		query = self.session.query(Word.eng, Word.rus, File.name).join(File)
		if fname:
			query = query.filter(File.name == fname)
		if eng:
			query = query.filter(Word.eng == eng)
		if rus:
			query = query.filter(Word.rus == rus)
		if updated_before:
			query = query.filter(Word.updated == None)
		if eng_pattern:
			query = query.filter(Word.eng.like("%" + eng_pattern + "%"))
		if max_passed:
			query = query.filter((Word.passed + Word.failed) < max_passed)
		if rate:
			query = query.filter(Word.tr_num + Word.ex_num + Word.ph_num >= rate)
		if max_passed or rate:
			query = query.order_by(Word.passed + Word.failed, Word.passed)
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

	# === # Hostory operations  # === #

	def getMaxCounter(self, counter):
		return self.session.query(func.max(getattr(Word, counter))).scalar()

	def getHistory(self, date, rate):
		stats = self.session.query(func.max(History.date), History.passed, History.failed)
		stats = stats.filter(History.date < date)
		if rate:
			word_ids = self.session.query(Word.id).filter(Word.tr_num + Word.ex_num + Word.ph_num >= rate)
			word_ids = map(lambda x: x[0], word_ids.all())
			stats = stats.filter(History.word.in_(word_ids))
		stats = stats.group_by(History.word)
		stats = stats.having(History.passed > -1)
		return map(lambda s: s[1:], stats.all())

	def getMinDate(self):
		return self.session.query(func.date(func.min(History.date))).scalar()

	def getMaxDate(self):
		return self.session.query(func.date(func.max(History.date))).scalar()

	def updateCounter(self, eng, counter):
		word = self.session.query(Word).filter(Word.eng == eng).one()
		count = int(getattr(word, counter)) + 1
		setattr(word, counter, count)
		history = History(date = getCurrentDateTime(), passed = word.passed, failed = word.failed)
		word.history.append(history)

	# === # Lingvo operations # === #

	def getLingvoStats(self, eng):
		word = self.session.query(Word).filter(Word.eng == eng).one()
		return word.tr_num, word.ex_num, word.ph_num, word.updated

	def setLingvoStats(self, eng, tr_num, ex_num, ph_num):
		word = self.session.query(Word).filter(Word.eng == eng).one()
		word.tr_num = tr_num
		word.ex_num = ex_num
		word.ph_num = ph_num
		word.updated = getCurrentDateTime()

	def createExamples(self, eng, examples):
		word = self.session.query(Word).filter(Word.eng == eng).one()
		for ex_eng, ex_rus in examples:
			example = self.session.query(Example).filter(Example.eng == ex_eng).first()
			if not example:
				example = Example(eng = ex_eng, rus = ex_rus)
				self.session.add(example)
				self.session.flush()
			word.examples.append(WordExample(word_id = word.id, example_id = example.id))

	def getExamples(self, eng = None):
		query = self.session.query(Example.eng, Example.rus)
		if eng:
			word = self.session.query(Word).filter(Word.eng == eng).one()
			example_ids = map(lambda x: x.example_id, word.examples)
			if not example_ids:
				return None
			query = query.filter(Example.id.in_(example_ids))
		return query.all()

	# === # Other operations # === #

	def getWordsByExample(self, eng):
		example = self.session.query(Example).filter(Example.eng == eng).one()
		word_ids = map(lambda x: x.word_id, example.words)
		if not word_ids:
			return None
		return self.session.query(Word.eng, Word.rus).filter(Word.id.in_(word_ids)).all()

	def getHistoryCountByDate(self, date_str):
		query = self.session.query(func.count(History.id)).filter(History.date.like(date_str + "%"))
		return query.filter((History.passed > 0) | (History.failed > 0)).scalar()
