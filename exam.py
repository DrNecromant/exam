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
parser.add_option("--stats", "-s", action="store_true",
	dest="stats", help="show stats")
parser.add_option("--difficulty", "-d", dest="d",
	default = "mixed", help="exam difficulty")
parser.add_option("--find", "-f", dest="eng",
	help="find word or part of word")
parser.add_option("--count", "-c", dest="count",
	default = 20, type = "int", help="number of word to exam")

(options, args) = parser.parse_args()

s = Storage(getDropboxPath())
xls = XLS()
dbpath = s.getFullPath("DB/translate.db")
db = DB(dbpath)

print "Sync data base..."
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
	sys.exit(0)
else:
	db.commit()

eng = options.eng
if eng:
	h.printWords(db.findWords(eng))
	sys.exit(0)

stats = options.stats
if stats:
	prefix = "stats_%s_" % date.today().isoformat()
	suffix = ".csv"
	fname = s.mkfile(prifix = prefix, suffix = suffix, dir = "Stats")
	fd = open(fname, "w+")
	writer = csv.writer(fd)
	writer.writerows(db.getStats())
	fd.close()
	print "Stats saved into %s" % fname
	sys.exit(0)

words = db.getAllWords()
count = options.count
if count:
	if options.d == "hard":
		words = words[:count * 2]
	elif options.d == "mixed":
		words = words[:count] + sample(words[count:], count)
	words = [words[0]] + sample(words[1:], count - 1)
shuffle(words)

unknown_words = list()
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
		db.updateCounter(q_word.encode("utf8"), "fail")
		unknown_words.append(word)
	db.updateCounter(eng, "count")
if unknown_words:
	prefix = "%s_%s_" % (testname, date.today().isoformat())
	suffix = ".xls"
	fname = s.mkfile(prifix = prefix, suffix = suffix, dir = "Translate")
	xls.dumpData(fname, unknown_words)
	print "Results have been saved into %s" % fname
db.commit()
