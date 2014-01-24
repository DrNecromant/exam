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

	def getErrors(self):
		errors = dict()
		duplicates = self._getDuplicates()
		if duplicates:
			errors["duplicates"] = map(lambda a: a.eng, duplicates)
		spaces = self._getSpaces()
		if spaces:
			errors["spaces"] = map(lambda a: a.eng, spaces)
		articles = self._getArticles()
		if articles:
			errors["articles"] = map(lambda a: a.eng, articles)
		engs = self._getEngs()
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

	def commit(self, fake = False):
		if fake:
			self_rollback()
		else:
			self._commit()
		self.changes = self.getBlankChanges()

	def updateCounter(self, eng, counter):
		self._updateCounter(eng, counter, self.getDateNow())
		self.changes["update"].append("%s %s %s" % (eng, counter, count))

	def updateSha(self, fname, sha):
		self._updateSha(fname, sha)
		self.changes["update"].append("%s | %s" % (fname, sha))

	def deleteFile(self, fname):
		words = self._getWordsFromFile(fname)
		for word in words:
			self.deleteWord(fname, word)
		self._deleteFile(fname)
		self.changes["delete"].append("%s | all words" % fname)

	def deleteWord(self, fname, eng):
		self._deleteWord(fname, eng, self.getDateNow())
		self.changes["delete"].append("%s | %s" % (fname, eng))

	def createFile(self, fname, sha, words):
		self._createFile(fname, sha)
		for word in words:
			eng, rus = word
			self.createWord(fname, eng, rus)
		self.changes["create"].append("%s | %s" % (fname, sha))

	def createWord(self, fname, eng, rus):
		self._createWord(fname, eng, rus, self.getDateNow())
		self.changes["create"].append("%s | %s | %s" % (fname, eng, rus))

	def updateWord(self, fname, eng, rus1, rus2):
		self._updateWord(fname, eng, rus2)
		self.changes["update"].append("%s | %s | %s -> %s" % (fname, eng, rus1, rus2))

	def getRawDataByDate(self, date):
		return self._getRawDataByDate(date + timedelta(1))

	def getDates(self):
		dates = self._getDates()
		min_date, max_date = map(lambda t: datetime.strptime(t, "%Y-%m-%d"), dates)
		dates = list()
		for i in range((max_date - min_date).days + 1):
			dates.append(min_date + timedelta(i))
		return dates
