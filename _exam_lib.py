# -*- coding: utf-8 -*-
import csv
from datetime import date
from lib import *

class Exam:
	__metaclass__ = h.DecoMeta
	def __init__(self, debug = False):
		self.s = Storage(getDropboxPath())
		self.xls = XLS()
		dbpath = self.s.getFullPath("DB/%s" % dbname)
		self.db = DB(dbpath)
		self.debug = debug

	def sync(self):
		xls_file_paths = self.s.getFiles(subdir = "Translate", fext = ".xls", exceptions = [testname])
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
			db.createFile(new_file_name, sha, xls_words)
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
			self.db.commit(fake = self.debug)

	def processDBWord(self, word):
		words = self.db.findWords(word)
		if not words:
			print "No word found"
		else:
			h.printWords(words)

	def saveStats(self):
		prefix = "stats_%s_" % date.today().isoformat()
		suffix = ".csv"
		fname = self.s.mkfile(prifix = prefix, suffix = suffix, dir = "Stats")
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
				self.db.updateCounter(q_word.encode("utf8"), "fail")
				unknown_words.append(word)
			self.db.updateCounter(eng, "count")
		self.processDBChanges()
		self.saveStats()
		if unknown_words:
			self.saveTestWords(unknown_words)

	def saveTestWords(self, words):
		prefix = "%s_%s_" % (testname, date.today().isoformat())
		suffix = ".xls"
		fname = self.s.mkfile(prifix = prefix, suffix = suffix, dir = "Translate")
		self.xls.dumpData(fname, words)
		print "Results have been saved into %s" % fname
