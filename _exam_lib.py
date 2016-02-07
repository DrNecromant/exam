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
		self.rate = self.options.rate
		self.s = Storage(getCloudPath())
		self.xls = XLS()
		self.dbpath = "%s/%s" % (DBDIR, DBNAME)
		self.db = DB(self.dbpath)
		self.fake = self.options.fake
		self.dict_words = list()

	def sync(self):
		xls_file_paths = self.s.getFiles(subdir = TRANSLATEDIR, fext = ".xls")
		xls_file_names = map(self.s.getShortPath, xls_file_paths)
		xls_set = set(xls_file_names)
		db_file_names = self.db.getFileNames()
		db_set = set(db_file_names)
		old_file_names = db_set - xls_set
		new_file_names = xls_set - db_set
		upd_file_names = xls_set & db_set

		for old_file_name in old_file_names:
			engs = self.db.getWords(fname = old_file_name, output = 1)
			for eng in engs:
				self.db.deleteWord(old_file_name, eng)
			self.db.deleteFile(old_file_name)
		for new_file_name in new_file_names:
			new_file_path = self.s.getFullPath(new_file_name)
			xls_words = self.xls.loadData(new_file_path)
			sha = self.s.getSha(new_file_name)
			self.db.createFile(new_file_name, sha)
			for eng, rus in xls_words:
				self.db.createWord(new_file_name, eng, rus)
		for upd_file_name in upd_file_names:
			db_sha = self.db.getFileSha(upd_file_name)
			xls_sha = self.s.getSha(upd_file_name)
			if db_sha == xls_sha:
				continue
			self.db.updateFileSha(upd_file_name, xls_sha)
			xls_words = self.xls.loadData(self.s.getFullPath(upd_file_name))
			xls_dict = dict(xls_words)
			db_words = self.db.getWords(fname = upd_file_name, output = 3)
			db_dict = dict(db_words)
			engs = set(xls_dict.keys()) | set(db_dict.keys())
			for eng in engs:
				xls_rus = xls_dict.get(eng)
				db_rus = db_dict.get(eng)
				if not xls_rus:
					self.db.deleteWord(upd_file_name, eng)
				elif not db_rus:
					self.db.createWord(upd_file_name, eng, xls_rus)
				elif xls_rus != db_rus:
					self.db.updateWord(upd_file_name, eng, db_rus, xls_rus)

	def applyChanges(self):
		if self.fake:
			self.db.rollback()
		else:
			self.db.commit()

	def processDBErrors(self):
		engs = self.db.getWords(output = 1)
		errors = h.getErrors(engs, checker = self.checkEngWord)
		if errors:
			h.printErrors(errors, self.db.getWords)
			return False
		else:
			self.applyChanges()
			return True

	def processDBWord(self, word):
		words = self.db.getWords(eng_pattern = word)
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
			self.applyChanges()
			h.randomSleep(delay/2, delay + delay/2)

	def setWordStats(self, eng):
		l = Lingvo(eng)
		if l.ex_num is None:
			raise Exception("Error in getting counters")
		if l.ex_num and not l.examples:
			raise Exception("Error in getting examples")
		self.db.setLingvoStats(eng, l.tr_num, l.ex_num, l.ph_num)
		if l.ex_num:
			self.updateExamples(eng, l.examples)

	def updateExamples(self, eng, examples):
		db_examples = self.db.getExamples(eng)
		if db_examples:
			examples_to_create = list()
			db_eng_examples = zip(*db_examples)[0]
			for ex_eng, ex_rus in examples:
				if ex_eng in db_eng_examples:
					continue
				examples_to_create.append((ex_eng, ex_rus))
			if examples_to_create:
				self.db.createExamples(eng, examples_to_create)
		else:
			self.db.createExamples(eng, examples)

	def doExam(self, count, phrase = False):
		if phrase:
			self.testPhrases(count = count)
		else:
			self.testWords(count = count)

	def testPhrases(self, count):
		phrases_to_exam = self.db.getExamples()
		phrases = h.sampleList(phrases_to_exam, count)
		for phrase in phrases:
			eng, rus = phrase
			print eng
			words = self.db.getWordsByExample(eng)
			for word in words:
				eng, rus = word
				print "\t%s %s" % (eng, rus)

	def testWords(self, count):
		words_to_exam = self.db.getWords(max_passed = PASSED_LIMIT, rate = self.rate)
		if not words_to_exam:
			print "# No words to exam"
			return
		print "# Check %s from %s words" %(count, len(words_to_exam))
		words = h.smartSelection(words_to_exam, count)
		for word in words:
			eng, rus, fname = word
			tr, ex, ph, update_date = self.db.getLingvoStats(eng)
			rank = tr + ex + ph if update_date else None

			raw_input("\n%s (%s)" % (eng, rank))
			print "%s" % fname
			answer = raw_input("%s\nDo you know? (y)/n: " % rus)
			if answer == "finish":
				print "Exit from exam with saving changes"
				break
			if answer:
				self.db.updateCounter(eng, "failed")
				hints = set()
				for w in eng.split():
					other_words = self.db.getWords(eng_pattern = w)
					if len(other_words) < 10:
						hints.update(other_words)
				if hints:
					h.printWords(hints)
				examples = self.db.getExamples(eng)
				if examples:
					examples = h.sampleList(examples, min(len(examples), 3))
					h.printExamples(examples)
			else:
				self.db.updateCounter(eng, "passed")
		self.applyChanges()

	def getStats(self):
		max_passed = self.db.getMaxCounter("passed")
		all_stats = list()
		mindate = self.db.getMinDate()
		maxdate = self.db.getMaxDate()
		dates = h.getDatesFromRange(mindate, maxdate)
		for date in dates:
			raw_data = self.db.getHistory(h.incDate(date), self.rate)
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

	def processWordCount(self, max_lines = 10):
		mindate, maxdate = self.db.getMinMaxDates()
		dates = h.getDatesFromRange(mindate, maxdate)
		stats = dict()
		for date in dates:
			date_str = date.strftime("%Y-%m-%d")
			count = self.db.getHistoryCountByDate(date_str)
			stats[date_str] = count
		h.printWordCount(stats, max_lines)
