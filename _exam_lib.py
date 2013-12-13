# -*- coding: utf-8 -*-

import csv
from datetime import datetime
from lib import *

class Exam:
	__metaclass__ = DecoMeta
	def __init__(self, fake = False):
		self.s = Storage(getDropboxPath())
		self.xls = XLS()
		self.dbpath = self.s.getFile(DBNAME, subdir = DBDIR)
		self.db = DB(self.dbpath)
		self.fake = fake

	def sync(self):
		xls_file_paths = self.s.getFiles(subdir = TRANSLATEDIR, fext = ".xls")
		xls_file_names = map(self.s.getShortPath, xls_file_paths)
		xls_set = set(xls_file_names)
		db_file_names = self.db.getAllFiles()
		db_set = set(db_file_names)
		old_file_names = db_set - xls_set
		new_file_names = xls_set - db_set
		upd_file_names = xls_set & db_set

		for old_file_name in old_file_names:
			self.db.deleteFile(old_file_name)
		for new_file_name in new_file_names:
			new_file_path = self.s.getFullPath(new_file_name)
			xls_words = self.xls.loadData(new_file_path)
			sha = self.s.getSha(new_file_name)
			self.db.createFile(new_file_name, sha, xls_words)
		for upd_file_name in upd_file_names:
			db_sha = self.db.getSha(upd_file_name)
			xls_sha = self.s.getSha(upd_file_name)
			if db_sha == xls_sha:
				continue
			self.db.updateSha(upd_file_name, xls_sha)
			xls_words = self.xls.loadData(self.s.getFullPath(upd_file_name))
			xls_dict = dict(xls_words)
			db_words = self.db.loadData(upd_file_name)
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

	def processDBErrors(self):
		errors = self.db.getErrors()
		if errors:
			h.printErrors(errors, self.db.getWords)
			return False
		else:
			self.processDBChanges()
			return True

	def processDBChanges(self):
		changes = self.db.getChanges()
		if changes == self.db.getBlankChanges():
			print "There is nothing to commit"
		else:
			h.printChanges(changes)
			self.db.commit(fake = self.fake)
			if not self.fake:
				self.s.mkClone(self.dbpath)

	def processDBWord(self, word):
		words = self.db.findWords(word)
		if not words:
			print "No word found"
		else:
			h.printWords(words)

	def saveCurrentStats(self):
		if self.fake:
			print "Cannot save stats - fake mode"
			return
		fname = self.s.getFile(name = "exam_stats.csv", subdir = STATSDIR)
		fd = open(fname, "w+")
		writer = csv.writer(fd)
		writer.writerows(self.db.getStats())
		fd.close()
		print "Stats have been saved into %s" % fname

	def doExam(self, count, rus):
		print "=== words count %s ===" % count
		unknown_words = list()
		words = h.smartSelection(self.db.getAllWords(), count)
		for word in words:
			q_word, a_word, fname = word
			eng = q_word
			if rus:
				q_word, a_word = a_word, q_word
			print "\n= #%s = " % (words.index(word) + 1)
			raw_input(q_word.encode("utf8"))
			print "%s" % fname.encode("utf8")
			answer = raw_input("%s\nDo you know? (y)/n: " % a_word.encode("utf8"))
			if answer:
				self.db.updateCounter(eng, "failed")
				unknown_words.append(word)
			else:
				self.db.updateCounter(eng, "passed")
		self.processDBChanges()
		if unknown_words:
			self.saveTestWords(unknown_words)

	def saveTestWords(self, words):
		if self.fake:
			print "Cannot save test words - fake mode"
			return
		prefix = "%s_%s_" % (TESTNAME, datetime.today().strftime(TIMEFORMAT))
		suffix = ".xls"
		fname = self.s.mkFile(prifix = prefix, suffix = suffix, subdir = TESTDIR)
		self.xls.dumpData(fname, words)
		print "Results have been saved into %s" % fname

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
			content = [word[0] for word in words if len(word) == 1]
			content = h.shuffleList(content)
			self.saveTestWords(content)
		self.s.unlinkFiles(testfiles)

	def getStats(self):
		dates = self.db.getDates()
		for date in dates:
			result = {
				"p_sum": 0,
				"f_sum": 0,
				"idle": 0,
				"bad": 0,
				"good": 0
			}
			stats = self.db.getStatsByDate(date)
			for passed, failed in stats:
				result["p_sum"] += passed
				result["f_sum"] += failed
				if passed == 0 and failed == 0:
					result["idle"] += 1
				elif passed > failed:
					result["good"] += 1
				else:
					result["bad"] += 1
			print date
			print result
