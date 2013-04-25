# -*- coding: utf-8 -*-
from os import path

import csv
from datetime import datetime
from random import randint, sample
from optparse import OptionParser
from time import time

from lib import *

parser = OptionParser()
parser.add_option("-l", "--list", action="store_true",
	dest="list", help="show list of files")
parser.add_option("-c", "--check", action="store_true",
	dest="check", help="check duplicates")
parser.add_option("-e", "--exam", action="store_true",
	dest="exam", help="exam yourself")
parser.add_option("-s", "--sync", action="store_true",
	dest="sync", help="sync with database")
parser.add_option("-j", "--join", action="store_true",
	dest="join", help="combine several files in one")
parser.add_option("-f", "--find", dest="word",
	help="find word or part of word")

(options, args) = parser.parse_args()

s = Storage(getDropboxPath())
xls = XLS()
dbpath = s.getFullPath("DB/translate.db")
db = DB(dbpath)

word = options.word
if word:
	words = db.getWord(word)
	if not words:
		print "Could not find"
	i = 0
	for eng, rus, fname in words:
		print "%s) %s" % (i, eng.encode("utf8"))
		print "\t%s" % rus.encode("utf8")
		print "\t%s" % fname.encode("utf8")
		i += 1

if options.list:
	db.printFileList()

if options.sync:
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
		db.sync(values)

if options.exam:
	print "\n=========="

	fs = None
	findices = raw_input("Files you want to check? (all)/numbers: ")
	if findices:
		fs = map(lambda i: int(i.strip()), findices.split())

	db.printFileList(files = fs)
	values = db.getValues(files = fs)
	length = len(values)
	print "words count: %s" % length

	count = raw_input("Count of words you want to check? (all)/number: ")
	if count:
		count = int(count)
		values = sample(values, count)
	else:
		count = length

	lang = raw_input("Lang you want to check? (en)/rus: ")
	if lang:
		x = 1
		y = 0
		resultfile = "results_ru.csv"
	else:
		x = 0
		y = 1
		resultfile = "results_en.csv"


	start = time()
	time_str = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
	ret = []
	j = 0
	while values:
		ret.append(len(values))
		test = list(values)
		j += 1
		l = len(test)
		i = 0
		while test:
			index = randint(0, len(test) - 1)
			word = test.pop(index)
			i += 1
			print "===== %s attempt: %s from %s" %(j, i, l)
			raw_input(word[x].encode("utf8"))
			print "%s" % word[2].encode("utf8")
			answer = raw_input("%s\nDo you know? (y)/n: " % word[y].encode("utf8"))
			if not answer:
				values.remove(word)
			print
		if j == 1 and values:
			answer = raw_input("Want to save unknown words? y/(n)? ")
			if answer:
				xls.dump(s.getFullPath("Translate/%s", testname), values)
			print
				
	end = time()
	t = end - start
	h = int(t)/3600
	m = (int(t)/60)%60
	s = int(t)%60
	print "result %s" % ret
	print "time: %sh %sm %ss" %(h, m, s)
	print "speed: %s words/hour" % int((count/t) * 3600)
	print "debug: %s seconds" % t
	# Save date, lenght, count, first result, time (seconds)
	print "\n=========="
	answer = raw_input("Want to save result? y/(n)? ")
	if answer:
		fd = open(resultfile, "a")
		w = csv.writer(fd)
		if len(ret) > 1:
			unknown = ret[1]
		else:
			unknown = 0
		w.writerow([time_str, length, count, unknown, int(t)])
		fd.close()
		print "Results have been saved into %s" % resultfile

db.quit()
