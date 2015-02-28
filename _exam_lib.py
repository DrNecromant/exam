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
parser.add_option("--rate", "-r", dest = "rate",
	default = 0, type = "int",
	help = "find words with rate more that rate")

class Exam:
	__metaclass__ = DecoMeta
	def __init__(self):
		(self.options, self.args) = parser.parse_args()
		if self.options.debug:
			config.debug = True
		self.s = Storage(getCloudPath())
		self.xls = XLS()
		self.dbpath = self.s.getFile(DBNAME, subdir = DBDIR)
		self.db = DB(self.dbpath, h.getDateNow, self.options.rate)
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
		outdated = h.getDateBefore(EXAMPLES_LIFETIME)
		engs = self.db.getWords(output = 1, updated_before = outdated)
		if not engs:
			print "No word to sync"
			return
		engs = list(engs)
		engs.reverse()
		count = len(engs) + 1
		for eng in engs:
			count -= 1
			print "[ Update %s ]" % count
			self.setWordStats(eng)
			self.processDBChanges()
			h.randomSleep(delay/2, delay + delay/2)

	def setWordStats(self, eng):
		l = Lingvo(eng)
		if l.ex_num is None:
			raise Exception("Error in getting counters")
		if l.ex_num and not l.examples:
			raise Exception("Error in getting examples")
		self.db.setLingvoCounters(eng, l.tr_num, l.ex_num, l.ph_num)
		if l.ex_num:
			self.db.updateExamples(eng, l.examples)

	def doExam(self, count):
		words_to_exam = self.db.getSortedWords(max_passed = PASSED_LIMIT)
		if not words_to_exam:
			print "# No words to exam"
			return
		print "# Check %s from %s words" %(count, len(words_to_exam))
		words = h.smartSelection(words_to_exam, count)
		for word in words:
			eng, rus, fname = word
			rank = self.db.getWordRank(eng)

			raw_input("\n%s (%s)" % (eng.encode("utf8"), rank))
			print "%s" % fname.encode("utf8")
			answer = raw_input("%s\nDo you know? (y)/n: " % rus.encode("utf8"))
			if answer == "finish":
				print "Exit from exam with saving changes"
				break
			if answer:
				self.db.changeCounter(eng, "failed")
				hints = set()
				for w in eng.split():
					other_words = self.db.findWords(w)
					if len(other_words) < 10:
						hints.update(other_words)
				if hints:
					h.printWords(hints)
				examples = self.db.getExamples(eng)
				if examples:
					examples = h.sampleList(examples, min(len(examples), 3))
					h.printExamples(examples)
			else:
				self.db.changeCounter(eng, "passed")
		self.processDBChanges()

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
		h.buildPlot(f1, stats[:2], labels = ["passed", "failed"])
		f2 = self.s.getFile("quality.png", subdir = STATSDIR)
		h.buildPlot(f2, stats[2:], labels = ["passed"])

	def getDictEngWords(self):
		if self.dict_words:
			return self.dict_words
		files = self.s.getFiles(subdir = DICTDIR, fext = ".xls")
		for f in files:
			data = self.xls.loadData(f, column_num = 1)
			for entry in data:
				self.dict_words.append(entry[0])
		return self.dict_words

	def checkEngWord(self, eng):
		if eng not in self.getDictEngWords():
			return False
		return True

	def processWordCount(self, date = h.getDateNow(), max_lines = 10):
		mindate, maxdate = self.db.getMinMaxDates()
		dates = h.getDatesFromRange(mindate, maxdate)
		stats = dict()
		for date in dates:
			date_str = date.strftime("%Y-%m-%d")
			count = self.db.getCountByDate(date_str)
			stats[date_str] = count
		h.printWordCount(stats, max_lines)
