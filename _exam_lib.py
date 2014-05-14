# -*- coding: utf-8 -*-

import csv
from datetime import datetime
from lib import *
from optparse import OptionParser

parser = OptionParser()
parser.add_option("--debug", "-d", action = "store_true",
	dest = "debug", help = "debug logs")
parser.add_option("--fake", "-k", action="store_true",
	dest="fake", help="dry run")

class Exam:
	__metaclass__ = DecoMeta
	def __init__(self):
		(self.options, self.args) = parser.parse_args()
		if self.options.debug:
			config.debug = True
		self.s = Storage(getDropboxPath())
		self.xls = XLS()
		self.dbpath = self.s.getFile(DBNAME, subdir = DBDIR)
		self.db = DB(self.dbpath, h.getDateNow)
		self.fake = self.options.fake
		self.dict_words = list()

	def sync(self):
		xls_file_paths = self.s.getFiles(subdir = TRANSLATEDIR, fext = ".xls")
		xls_file_names = map(self.s.getShortPath, xls_file_paths)
		xls_set = set(xls_file_names)
		db_file_names = self.db.getFiles()
		db_set = set(db_file_names)
		old_file_names = db_set - xls_set
		new_file_names = xls_set - db_set
		upd_file_names = xls_set & db_set

		for old_file_name in old_file_names:
			self.db.removeFile(old_file_name)
		for new_file_name in new_file_names:
			new_file_path = self.s.getFullPath(new_file_name)
			xls_words = self.xls.loadData(new_file_path)
			sha = self.s.getSha(new_file_name)
			self.db.addFile(new_file_name, sha, xls_words)
		for upd_file_name in upd_file_names:
			db_sha = self.db.getSha(upd_file_name)
			xls_sha = self.s.getSha(upd_file_name)
			if db_sha == xls_sha:
				continue
			self.db.changeSha(upd_file_name, xls_sha)
			xls_words = self.xls.loadData(self.s.getFullPath(upd_file_name))
			xls_dict = dict(xls_words)
			db_words = self.db.getWords(fname = upd_file_name, output = 3)
			db_dict = dict(db_words)
			engs = set(xls_dict.keys()) | set(db_dict.keys())
			for eng in engs:
				xls_rus = xls_dict.get(eng)
				db_rus = db_dict.get(eng)
				if not xls_rus:
					self.db.removeWord(upd_file_name, eng)
				elif not db_rus:
					self.db.addWord(upd_file_name, eng, xls_rus)
				elif xls_rus != db_rus:
					self.db.changeWord(upd_file_name, eng, db_rus, xls_rus)

	def processDBErrors(self):
		engs = self.db.getWords(output = 1)
		errors = h.getErrors(engs, checker = self.checkEngWord)
		if errors:
			h.printErrors(errors, self.db.getWords)
			return False
		else:
			self.processDBChanges()
			return True

	def processDBChanges(self):
		changes = self.db.getChanges()
		if changes != self.db.getBlankChanges():
			h.printChanges(changes)
			self.db.applyChanges(fake = self.fake)
			if not self.fake:
				self.s.mkClone(self.dbpath)

	def processDBWord(self, word):
		words = self.db.findWords(word)
		if words:
			h.printWords(words)

	def processLingvoWords(self, delay):
		i = 0
		engs = self.db.getWords(output = 1)
		for eng in engs:
			rank, date = self.db.getWordRank(eng)
			print eng, rank, date
			if rank is None or h.getDaysFrom(date) >= 7:
				i += 1
				print "\tUpdate", i
				result = self.setWordStats(eng)
				if not result:
					break
				self.processDBChanges()
				h.randomSleep(delay/2, delay + delay/2)
			else:
				print "Already synced"

	def setWordStats(self, eng):
		l = Lingvo(eng)
		if l.examples is None:
			print "\tError in getting counters"
			return False
		if l.examples and not l.ex_list:
			print "\tError in getting examples"
			return False
		self.db.setLingvoCounters(eng, l.translations, l.examples, l.phrases)
		if l.examples:
			self.db.updateExamples(eng, l.ex_list)
		print "\tSuccess"
		return True

	def doExam(self, count, rus):
		words_to_exam = self.db.getSortedWords(max_passed = PASSED_LIMIT)
		if not words_to_exam:
			print "# No words to exam"
			return
		print "# Check %s from %s words" %(count, len(words_to_exam))
		unknown_words = list()
		words = h.smartSelection(words_to_exam, count)
		for word in words:
			q_word, a_word, fname = word
			eng = q_word
			rank = self.db.getWordRank(eng)[0]

			if rus:
				q_word, a_word = a_word, q_word
			print "\n= #%s = " % (words.index(word) + 1)
			raw_input(q_word.encode("utf8") + " (%s)" % rank)
			print "%s" % fname.encode("utf8")
			answer = raw_input("%s\nDo you know? (y)/n: " % a_word.encode("utf8"))
			if answer == "finish":
				print "Exit from exam with saving changes"
				break
			if answer:
				self.db.changeCounter(eng, "failed")
				unknown_words.append(word)
				hints = set()
				for w in eng.split():
					other_words = self.db.findWords(w)
					if len(other_words) < 10:
						hints.update(other_words)
				if hints:
					h.printWords(hints)
			else:
				self.db.changeCounter(eng, "passed")
		self.processDBChanges()
		if unknown_words:
			self.saveTestWords(unknown_words)

	def saveTestWords(self, words):
		if self.fake:
			return
		prefix = "%s_%s_" % (TESTNAME, datetime.today().strftime(TIMEFORMAT))
		suffix = ".xls"
		fname = self.s.mkFile(prifix = prefix, suffix = suffix, subdir = TESTDIR)
		self.xls.dumpData(fname, words)

	def joinTestFiles(self):
		engs = set()
		testfiles = self.s.getFiles(subdir = TESTDIR, fext = ".xls")
		for testfile in testfiles:
			# get third columns values to remove marked words
			words = self.xls.loadData(testfile, column_num = 3)
			for word in words:
				if len(word) > 2 and word[2]:
					continue
				engs.add(word[0])
		words = map(self.db.getWords, engs)
		if words:
			content = [word[0] for word in words if word and len(word) == 1]
			content = h.shuffleList(content)
			self.saveTestWords(content)
		self.s.unlinkFiles(testfiles)

	def getStats(self):
		max_passed = self.db.getMaxPassed()
		all_stats = list()
		mindate, maxdate = self.db.getMinMaxDates()
		dates = h.getDatesFromRange(mindate, maxdate)
		for date in dates:
			raw_data = self.db.getRawDataByDate(h.incDate(date))
			stats = h.getStatsFromRawData(raw_data, max_passed)
			all_stats.append(stats)
		return zip(*all_stats)

	def buildPlot(self, stats):
		f1 = self.s.getFile("quantity.png", subdir = STATSDIR)
		h.buildPlot(f1, stats[:2])
		f2 = self.s.getFile("quality.png", subdir = STATSDIR)
		h.buildPlot(f2, stats[2:])

	def getDictEngWords(self):
		if self.dict_words:
			return self.dict_words
		files = self.s.getFiles(subdir = DICTDIR, fext = ".xls")
		for f in files:
			data = self.xls.loadData(f, column_num = 1)
			for entry in data:
				dict_words.append(entry[0])
		return self.dict_words

	def checkEngWord(self, eng):
		if eng not in self.getDictEngWords():
			return False
		return True

	def printProcessedWordCount(self, date = h.getDateNow()):
		date_str = date.strftime("%Y-%m-%d")
		count = self.db.getCountByDate(date_str)
		print count
