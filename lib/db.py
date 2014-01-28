from _base_db import _base_DB
from datetime import datetime, timedelta

class DB(_base_DB):
	def __init__(self, dbpath):
		_base_DB.__init__(self, dbpath)
		self.changes = self.getBlankChanges()
		self.now = None

	def getDateNow(self):
		if not self.now:
			self.now = datetime.now().replace(microsecond = 0)
		return self.now

	def getChanges(self):
		return dict(self.changes)

	def getBlankChanges(self):
		return {"create": list(), "update": list(), "delete": list()}

	def commit(self, fake = False):
		if fake:
			self_rollback()
		else:
			self._commit()
		self.changes = self.getBlankChanges()

	def updateCounter(self, eng, counter):
		self.updateCounterWithDate(eng, counter, self.getDateNow())
		self.changes["update"].append("%s %s %s" % (eng, counter, count))

	def updateSha(self, fname, sha):
		self.updateShaByFile(fname, sha)
		self.changes["update"].append("%s | %s" % (fname, sha))

	def deleteFile(self, fname):
		words = self.getWordsByFile(fname)
		for word in words:
			self.deleteWord(fname, word.eng)
		self.deleteFileByName(fname)
		self.changes["delete"].append("%s | all words" % fname)

	def deleteWord(self, fname, eng):
		self.deleteWordWithDate(fname, eng, self.getDateNow())
		self.changes["delete"].append("%s | %s" % (fname, eng))

	def createFile(self, fname, sha, words):
		self.createFileWithSha(fname, sha)
		for word in words:
			eng, rus = word
			self.createWord(fname, eng, rus)
		self.changes["create"].append("%s | %s" % (fname, sha))

	def createWord(self, fname, eng, rus):
		self.createWordWithDate(fname, eng, rus, self.getDateNow())
		self.changes["create"].append("%s | %s | %s" % (fname, eng, rus))

	def updateWord(self, fname, eng, rus1, rus2):
		self.updateWordRus(fname, eng, rus2)
		self.changes["update"].append("%s | %s | %s -> %s" % (fname, eng, rus1, rus2))

	def getRawDataByDate(self, date):
		return self.getHistoryByDate(date + timedelta(1))

	def getDates(self):
		dates = self.getDatesMinMax()
		min_date, max_date = map(lambda t: datetime.strptime(t, "%Y-%m-%d"), dates)
		dates = list()
		for i in range((max_date - min_date).days + 1):
			dates.append(min_date + timedelta(i))
		return dates

	def getWords(self, name = None):
		if name:
			return self.getWordsByName(name)
		else:
			return self.getWordsEng()
