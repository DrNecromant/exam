from _base_db import _base_DB

class DB(_base_DB):
	def __init__(self, dbpath, timestamp):
		_base_DB.__init__(self, dbpath)
		self.changes = self.getBlankChanges()
		self.now = timestamp

	def getBlankChanges(self):
		return {"create": list(), "update": list(), "delete": list()}

	def getChanges(self):
		return dict(self.changes)

	# === # Main operations # === #

	def applyChanges(self, fake = False):
		if fake:
			self.rollback()
		else:
			self.commit()
		self.changes = self.getBlankChanges()

	def quit(self):
		self.close()

	# === # File operations # === #

	def addFile(self, name, sha, words):
		self.createFile(name, sha)
		for word in words:
			eng, rus = word
			self.addWord(name, eng, rus)
		self.changes["create"].append("%s" % name)

	def removeFile(self, name):
		engs = self.getWords(fname = name, output = 1)
		for eng in engs:
			self.removeWord(name, eng)
		self.deleteFile(name)
		self.changes["delete"].append("%s" % name)

	def getFiles(self):
		return self.getFileNames()

	def changeSha(self, fname, sha):
		self.updateFileSha(fname, sha)
		self.changes["update"].append("%s | %s" % (fname, sha))

	def getSha(self, fname):
		return self.getFileSha(fname)

	# === # Word operations # === #

	def addWord(self, fname, eng, rus):
		self.createWord(fname, eng, rus, self.now)
		self.changes["create"].append("%s | %s | %s" % (fname, eng, rus))

	def removeWord(self, fname, eng):
		self.deleteWord(fname, eng, self.now)
		self.changes["delete"].append("%s | %s" % (fname, eng))

	def changeWord(self, fname, eng, rus1, rus2):
		self.updateWord(fname, eng, rus2)
		self.changes["update"].append("%s | %s | %s -> %s" % (fname, eng, rus1, rus2))

	def getWords(self, eng = None, rus = None, fname = None, output = 7):
		return self.getWordEntries(eng, rus, fname, output)

	def findWords(self, eng):
		return self.getWordsLike(eng)

	def getSortedWords(self, max_passed):
		return self.getWordsByStats(max_passed)

	# === # Stats operations # === #

	def getMaxPassed(self):
		return self.getMaxCounter("passed")

	def getRawDataByDate(self, date):
		return self.getHistoryByDate(date)

	def getDatesMinMax(self):
		return self.getMinDate(), self.getMaxDate()

	def changeCounter(self, eng, counter):
		self.updateCounter(eng, counter, self.now)
		self.changes["update"].append("%s %s" % (eng, counter))

	def getMinMaxDates(self):
		return self.getMinDate(), self.getMaxDate()

	def getCountByDate(self, date_str):
		return self.getHistoryCountByDate(date_str)

	# === # Lingvo operations # === #

	def getLingvoCounters(self, eng):
		return self.getWordStats(eng)

	def setLingvoCounters(self, eng, translation, examples, phrases):
		self.setWordStats(eng, translation, examples, phrases, self.now)
		self.changes["update"].append("%s | %s | %s | %s" % (eng, translation, examples, phrases))

	def updateExamples(self, eng, examples):
		self.deleteExamples(eng)
		self.createExamples(eng, examples)
		self.changes["update"].append("%s | examples | %s" % (eng, len(examples)))

	def getWordRank(self, eng):
		tr, ex, ph, date = self.getLingvoCounters(eng)
		if date is None:
			return (None, None)
		return (tr + ex + ph, date)

	# === # Dict operations  # === #

	def addDictWord(self, eng):
		self.createDictEngWord(eng)
		self.changes["create"].append(eng)

	def getDictWords(self, eng):
		return self.getDictEngWords(eng)
