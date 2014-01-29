from _base_db import _base_DB
from datetime import datetime, timedelta

class DB(_base_DB):
	def __init__(self, dbpath):
		_base_DB.__init__(self, dbpath)
		self.changes = self.getBlankChanges()
		self.now = None

	# === # File operations # === #

	def addFile(self, name, sha, words):
		self.createFile(name, sha)
		for word in words:
			eng, rus = word
			self.createWord(name, eng, rus)
		self.changes["create"].append("%s" % name)

	def removeFile(self, name):
		engs = self.getWords(fname = name, output = 1)
		for eng in engs:
			self.removeWord(name, eng)
		self.deleteFile(name)
		self.changes["delete"].append("%s" % name)

	def getFiles(self):
		return self.getFileNames()

	def updateSha(self, fname, sha):
		self.updateFileSha(fname, sha)
		self.changes["update"].append("%s | %s" % (fname, sha))

	def getSha(self, fname):
		return self.getFileSha(fname)

	# === # Word operations # === #

	def addWord(self, fname, eng, rus):
		self.createWord(fname, eng, rus, self.getDateNow())
		self.changes["create"].append("%s | %s | %s" % (fname, eng, rus))

	def removeWord(self, fname, eng):
		self.deleteWord(fname, eng, self.getDateNow())
		self.changes["delete"].append("%s | %s" % (fname, eng))

	def changeWord(self, fname, eng, rus1, rus2):
		self.updateWord(fname, eng, rus2)
		self.changes["update"].append("%s | %s | %s -> %s" % (fname, eng, rus1, rus2))

	def getWords(self, eng = None, rus = None, fname = None, output = 7):
		return self.getWordEntries(eng, rus, fname, output)

	def findWords(self, eng):
		return self.getWordsLike(self, eng)

	def getSortedWords(self, max_passed = 5):
		return self.getWordsByStats(max_passed)

	# === # === # === #

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

	def getRawDataByDate(self, date):
		return self.getHistoryByDate(date + timedelta(1))

	def getDates(self):
		dates = self.getDatesMinMax()
		min_date, max_date = map(lambda t: datetime.strptime(t, "%Y-%m-%d"), dates)
		dates = list()
		for i in range((max_date - min_date).days + 1):
			dates.append(min_date + timedelta(i))
		return dates
