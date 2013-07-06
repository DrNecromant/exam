# -*- coding: utf-8 -*-
import csv
from datetime import datetime
from random import randint, sample
from optparse import OptionParser

from lib import *

parser = OptionParser()
parser.add_option("-e", "--exam", action="store_true",
	dest="exam", help="exam yourself")
parser.add_option("-r", "--rus", action="store_true",
	dest="rus", help="exam rus words")
parser.add_option("-s", "--sync", action="store_true",
	dest="sync", help="sync with database")
parser.add_option("-f", "--find", dest="eng",
	help="find word or part of word")

(options, args) = parser.parse_args()

s = Storage(getDropboxPath())
xls = XLS()
dbpath = s.getFullPath("DB/translate.db")
db = DB(dbpath)

eng = options.eng
if eng:
	h.printWords(db.findWords(eng))

if options.sync:
	xls_file_paths = s.getFiles(subdir = "Translate", fext = ".xls", exceptions = [testname])
	xls_file_names = map(s.getShortPath, xls_file_paths)
	xls_set = set(xls_file_names)
	db_file_names = db.getAllFiles()
	db_set = set(db_file_names)
	old_file_names = db_set - xls_set
	new_file_names = xls_set - db_set
	upd_file_names = xls_set & db_set

	for old_file_name in old_file_names:
		db.deleteFile(old_file_name)
	for new_file_name in new_file_names:
		new_file_path = s.getFullPath(new_file_name)
		xls_words = xls.loadData(new_file_path)
		sha = s.getSha(new_file_name)
		db.createFile(new_file_name, sha, xls_words)
	for upd_file_name in upd_file_names:
		db_sha = db.getSha(upd_file_name)
		xls_sha = s.getSha(upd_file_name)
		if db_sha == xls_sha:
			continue
		db.updateSha(upd_file_name, xls_sha)
		xls_words = xls.loadData(s.getFullPath(upd_file_name))
		xls_dict = dict(xls_words)
		db_words = db.loadData(upd_file_name)
		db_dict = dict(db_words)
		engs = set(xls_dict.keys()) | set(db_dict.keys())
		for eng in engs:
			xls_rus = xls_dict.get(eng)
			db_rus = db_dict.get(eng)
			if not xls_rus:
				db.deleteWord(upd_file_name, eng)
			elif not db_rus:
				db.createWord(upd_file_name, eng, xls_rus)
			elif xls_rus != db_rus:
				db.updateWord(upd_file_name, eng, db_rus, xls_rus)

	errors = db.getErrors()
	if errors:
		for error_type in errors:
			print "========== ERROR %s ==========" % error_type
			for eng in errors[error_type]:
				h.printWords(db.getWords(eng))
	else:
		db.commit()

if options.exam:
	words = db.getAllWords()

	count = raw_input("Count of words you want to check? (all)/number: ")
	if count:
		count = int(count)
		words = sample(words, count)
	else:
		count = len(words)

	j = 0
	while words:
		test = list(words)
		j += 1
		l = len(test)
		i = 0
		while test:
			index = randint(0, len(test) - 1)
			q_word, a_word, fname = word = test.pop(index)
			eng = q_word
			if options.rus:
				q_word, a_word = a_word, q_word
			i += 1
			print "===== %s attempt: %s from %s" %(j, i, l)
			raw_input(q_word.encode("utf8"))
			print "%s" % fname.encode("utf8")
			answer = raw_input("%s\nDo you know? (y)/n: " % a_word.encode("utf8"))
			if not answer:
				words.remove(word)
				db.updateCounter(eng, "success")
			db.updateCounter(eng, "count")
			print
		if j == 1 and words:
			answer = raw_input("Want to save unknown words? y/(n)? ")
			if answer:
				xls.dumpData(s.getFullPath("Translate/%s" % testname), words)
				print "Results have been saved into %s" % testname

	db.commit()

db.quit()
