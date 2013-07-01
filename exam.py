# -*- coding: utf-8 -*-
from os import path

import csv
from datetime import datetime
from random import randint, sample
from optparse import OptionParser

from lib import *

parser = OptionParser()
parser.add_option("-l", "--list", action="store_true",
	dest="list", help="show list of files")
parser.add_option("-e", "--exam", action="store_true",
	dest="exam", help="exam yourself")
parser.add_option("-r", "--rus", action="store_true",
	dest="rus", help="exam rus words")
parser.add_option("-j", "--join", action="store_true",
	dest="join", help="join files for test")
parser.add_option("-s", "--sync", action="store_true",
	dest="sync", help="sync with database")
parser.add_option("-f", "--find", dest="word",
	help="find word or part of word")

(options, args) = parser.parse_args()

s = Storage(getDropboxPath())
xls = XLS()
dbpath = s.getFullPath("DB/translate.db")
db = DB(dbpath)

word = options.word
if word:
	h.printValues(db.findValues(word))

if options.list:
	h.printFiles(db.getFiles())

if options.join:
	findices = raw_input("Files you want to check? (all)/numbers: ")
	if findices:
		fs = map(lambda i: int(i.strip()), findices.split())
		h.printFiles(db.getFiles(files = fs))
		xls.dump(s.getFullPath("Translate/%s" % testname), db.getValues(files = fs))
		print "Results have been saved into %s" % testname
	else:
		print "No files to store"

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
		db.createFile(new_file_name, xls_words)
	for upd_file_name in upd_file_names:
		upd_file_path = s.getFullPath(upd_file_name)
		db_sha = db.getSha(upd_file_name)
		sha = h.getSha(upd_file_path)
		if db_sha != sha:
			db.updateSha(upd_file_name, sha)
			xls_words = xls.loadData(upd_file_path)
			xls_engs = zip(*xls_words)[0]
			db_words = db.loadData(upd_file_name)
			db_engs = zip(*db_words)[0]
			xls_set = set(xls_words)
			db_set = set(db_words)
			old_words = set([word for word in db_set - xls_set if word[0] not in xls_engs])
			new_words = set([word for word in xls_set - db_set if word[0] not in db_engs])
			upd_words = (xls_set ^ db_set) - new_words - old_words
			for old_word in old_words:
				db.deleteWord(old_word)
			for new_word in new_words:
				db.createWord(upd_file_name, new_word)
			for upd_word in upd_words:
				db.updateWord(upd_file_name, upd_word)

	files = s.getFiles(subdir = "Translate", fext = ".xls", exceptions = [testname])
	values = map(lambda x: (x[0], x[1], s.getShortPath(x[2])), xls.load(files))
	engs = zip(*values)[0]
	check = [name for name in engs if engs.count(name) > 1]
	check = list(set(check))

	for word in check:
		similar = [v[1:] for v in values if v[0] == word]
		print "==> %s <==" % word
		for s in similar:
			print "\t%s" % s[0].encode("utf8")
			print "\t%s" % s[1].encode("utf8")

	if not check:
		db.syncValues(values)

if options.exam:
	print "\n=========="

	fs = None
	findices = raw_input("Files you want to check? (all)/numbers: ")
	if findices:
		fs = map(lambda i: int(i.strip()), findices.split())

	h.printFiles(db.getFiles(files = fs))
	values = db.getValues(files = fs)

	count = raw_input("Count of words you want to check? (all)/number: ")
	if count:
		count = int(count)
		values = sample(values, count)
	else:
		count = len(values)

	j = 0
	while values:
		test = list(values)
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
				values.remove(word)
				db.updateCounter(eng, "success")
			db.updateCounter(eng, "count")
			print
		if j == 1 and values:
			answer = raw_input("Want to save unknown words? y/(n)? ")
			if answer:
				xls.dump(s.getFullPath("Translate/%s" % testname), values)
				print "Results have been saved into %s" % testname
			print

	db.commit()

db.quit()
