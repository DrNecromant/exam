# -*- coding: utf-8 -*-
import sys

import csv
from datetime import date
from random import randint, sample, shuffle
from optparse import OptionParser

from lib import *

parser = OptionParser()
parser.add_option("--rus", "-r", action="store_true",
	dest="rus", help="exam rus words")
parser.add_option("--debug", "-d", action="store_true",
	dest="debug", help="dry run")
parser.add_option("--find", "-f", dest="find",
	help="find word or part of word")
parser.add_option("--count", "-c", dest="count",
	default = 20, type = "int", help="number of word to exam")

(options, args) = parser.parse_args()

class Exam:
	def __init__(self, debug = False):
		self.s = Storage(getDropboxPath())
		self.xls = XLS()
		dbpath = self.s.getFullPath("DB/translate.db")
		self.db = DB(dbpath)
		self.debug = debug

	def sync(self):
		print "Sync data base..."
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
			for error_type in errors:
				print "========== ERROR %s ==========" % error_type
				for eng in errors[error_type]:
					h.printWords(exam.getDBWords(eng))
			return False
		else:
			exam.applyDBChanges()
			return True

	def applyDBChanges(self):
		self.db.commit(fake = self.debug)

	def findDBWords(self, word):
		return self.db.findWords(word)

	def getDBWords(self, word):
		return self.db.getWords(word)

	def saveStats(self):
		prefix = "stats_%s_" % date.today().isoformat()
		suffix = ".csv"
		fname = self.s.mkfile(prifix = prefix, suffix = suffix, dir = "Stats")
		fd = open(fname, "w+")
		writer = csv.writer(fd)
		writer.writerows(self.db.getStats())
		fd.close()
		print "Stats have been saved into %s" % fname

	def getWords(self, count):
		words = self.db.getAllWords()
		words = words[:count] + sample(words[count:], count)
		index = count / 4
		words = words[:index] + sample(words[index:], count - index)
		shuffle(words)
		return words

	def doExam(self, count):
		print "=== words count %s ===" % count
		unknown_words = list()
		words = self.getWords(count)
		while words:
			l = len(words)
			index = randint(0, l - 1)
			q_word, a_word, fname = word = words.pop(index)
			eng = q_word
			if options.rus:
				q_word, a_word = a_word, q_word
			print "\n= %s words left = " % l
			raw_input(q_word.encode("utf8"))
			print "%s" % fname.encode("utf8")
			answer = raw_input("%s\nDo you know? (y)/n: " % a_word.encode("utf8"))
			if answer:
				self.db.updateCounter(q_word.encode("utf8"), "fail")
				unknown_words.append(word)
			self.db.updateCounter(eng, "count")
		self.applyDBChanges()
		self.saveStats()
		if unknown_words:
			exam.saveTestWords(unknown_words)

	def saveTestWords(self, words):
		prefix = "%s_%s_" % (testname, date.today().isoformat())
		suffix = ".xls"
		fname = self.s.mkfile(prifix = prefix, suffix = suffix, dir = "Translate")
		self.xls.dumpData(fname, words)
		print "Results have been saved into %s" % fname

exam = Exam(debug = options.debug)
exam.sync()
if not exam.processDBErrors():
	pass
elif options.find:
	h.printWords(exam.findDBWords(options.find))
else:
	exam.doExam(options.count)
