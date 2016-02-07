from random import sample, shuffle, randint
from collections import Counter, defaultdict
from enchant import Dict
from datetime import datetime, timedelta
import re
from time import sleep
from consts import *
import re

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
		print "%s) %s | %s | %s" % (i, eng, rus, sfname)

def printErrors(errors, mapper):
	for error_type in errors:
		print "========== ERROR %s (%s) ==========" % (error_type, len(errors[error_type]))
		for eng in errors[error_type]:
			printWords(mapper(eng))

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
	dict_us = Dict("en_US")
	dict_en = Dict("en_GB")
	for el, c in cnt.items():
		if len(el) < 3:
			errors["small_word"].append(el)
		if c > 1:
			errors["duplicates"].append(el)
		if el.startswith(" ") or el.endswith(" ") or "  " in el:
			errors["spaces"].append(el)
		if el.startswith("the ") or el.startswith("a ") or el.startswith("to "):
			errors["articles"].append(el)
		for ch in el:
			if ord(ch) >= 128:
				errors["rus_letters"].append(el)
				break
		for ch in "?!,.():;":
			if ch in el:
				errors["unused_signs"].append(el)
				break
		for w in re.findall("[\w']+", el):
			if not (dict_us.check(w) or dict_en.check(w) or checker(w) or w.isdigit()):
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
	res = list()
	for key in range(max_passed + 1):
		if key in stat_dict:
			if key == 0:
				# summarize all passed words insdead of all not passed in key 0
				res.append(total - stat_dict[key])
			else:
				res.append(stat_dict[key])
		else:
			res.append(0)
	res = [p_sum, f_sum] + res
	return res

def buildPlot(file_to_save, stats, labels = []):
	plt.figure(file_to_save)
	plt.grid()
	i = 0
	for stat in stats:
		x = i - len(labels) + 1
		if x > 0:
			label = "line %s" % x
		else:
			label = labels[i]
		plt.plot(stat, label = label)
		i += 1
	plt.legend(loc='upper left')
	plt.savefig(file_to_save)

def getCurrentDateTime():
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

def printWordCount(stats, max_lines):
	for date in sorted(stats)[-max_lines:]:
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
