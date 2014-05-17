from random import sample, shuffle, randint
from collections import Counter, defaultdict
from enchant import Dict
from datetime import datetime, timedelta
import re
from time import sleep
from consts import *

import numpy as np
import matplotlib.pyplot as plt

import htmlentitydefs

def printWords(words):
	print "*** Words ***"
	if not words:
		print "Could not find"
		return
	i = 0
	for eng, rus, fname in words:
		i += 1
		sfname = fname.replace(TRANSLATEDIR, "")[1:]
		print "%s) %s | %s | %s" % (i, eng.encode("utf8"), rus.encode("utf8"), sfname.encode("utf8"))

def printErrors(errors, mapper):
	for error_type in errors:
		print "========== ERROR %s (%s) ==========" % (error_type, len(errors[error_type]))
		for eng in errors[error_type]:
			printWords(mapper(eng))

def printChanges(changes):
	for ctype in changes:
		if changes[ctype]:
			print "========== %s ===========" % ctype
		for c in changes[ctype]:
			print "==> %s" % c

def smartSelection(l, c):
	if len(l) <= c * 3:
		res = l[:c]
	else:
		x = c / 3
		y = c * 3
		z = c - x * 2
		res = l[:x] + sample(l[x:y], x) + sample(l[y:], z)
	shuffle(res)
	return res

def shuffleList(l):
	shuffle(l)
	return l

def sampleList(l, n):
	return sample(l, n)

def getErrors(l, checker):
	errors = defaultdict(list)
	cnt = Counter(l)
	dict_en = Dict("en_US")
	for el, c in cnt.items():
		if len(el) < 3:
			errors["small_word"].append(el)
		if c > 1:
			errors["duplicates"].append(el)
		if el.startswith(" ") or el.endswith(" ") or "  " in el:
			errors["spaces"].append(el)
		if el.startswith("the ") or el.startswith("a "):
			errors["articles"].append(el)
		for ch in el:
			if ord(ch) >= 128:
				errors["rus_letters"].append(el)
				break
		for ch in "?!,.():;":
			if ch in el:
				errors["unused_signs"].append(el)
				break
		for w in el.split():
			if not dict_en.check(w) and not checker(w) and not w.isdigit():
				errors["invalid"].append(el)
	return errors

def getStatsFromRawData(data, max_passed):
	stat_dict = dict()
	p_sum = f_sum = total = 0
	for passed, failed in data:
		p_sum += passed
		f_sum += failed
		total += 1
		if stat_dict.has_key(passed):
			stat_dict[passed] += 1
		else:
			stat_dict[passed] = 1
	res = [p_sum, f_sum]
	for key in range(max_passed + 1):
		if key in stat_dict:
			res.append(stat_dict[key])
		else:
			res.append(0)
	res.append(total)
	return res

def buildPlot(file_to_save, stats):
	plt.figure(file_to_save)
	plt.grid()
	i = 0
	for stat in stats:
		plt.plot(stat, label = "line %s" % i)
		i += 1
	plt.legend(loc='upper left')
	plt.savefig(file_to_save)

def getDateNow():
	return datetime.now().replace(microsecond = 0)

def getDatesFromRange(mindate, maxdate):
	convert_date = lambda t: datetime.strptime(t, "%Y-%m-%d")
	mindate = convert_date(mindate)
	maxdate = convert_date(maxdate)
	dates = list()
	for i in range((maxdate - mindate).days + 1):
		dates.append(mindate + timedelta(i))
	return dates

def getDateBefore(days):
	return getDateNow() - timedelta(days)

def incDate(date):
	return date + timedelta(1)

def unescape(text):
   def fixup(m):
      text = m.group(0)
      if text[:2] == "&#":
         # character reference
         try:
            if text[:3] == "&#x":
               return unichr(int(text[3:-1], 16))
            else:
               return unichr(int(text[2:-1]))
         except ValueError:
            pass
      else:
         # named entity
         try:
            if text[1:-1] == "amp":
               text = "&amp;amp;"
            elif text[1:-1] == "gt":
               text = "&amp;gt;"
            elif text[1:-1] == "lt":
               text = "&amp;lt;"
            else:
               key = text[1:-1]
               text = unichr(htmlentitydefs.name2codepoint[key])
         except KeyError:
            pass
      return text
   return re.sub("&#?\w+;", fixup, text)

def randomSleep(begin, end):
	t = randint(begin, end)
	sleep(t)

def printWordCount(stats):
	for date in sorted(stats)[:5]:
		print date, ":", stats[date]
	values = stats.values()
	average = sum(values) / len(values) 
	print "average :", average

def printExamples(examples):
	print "*** Examples ***"
	i = 0
	for example in examples:
		i += 1
		eng, rus = example
		print "%s) %s" % (i, eng)
		print "\t%s" % rus
