from random import sample, shuffle
from collections import Counter, defaultdict
from enchant import Dict

import numpy as np
import matplotlib.pyplot as plt

def printWords(words):
	if not words:
		print "Could not find"
		return
	for eng, rus, fname in words:
		print "%s | %s" % (eng.encode("utf8"), rus.encode("utf8"))
		print "\t%s" % fname

def printErrors(errors, mapper):
	for error_type in errors:
		print "========== ERROR %s ==========" % error_type
		for eng in errors[error_type]:
			printWords(mapper(eng))

def printChanges(changes):
	for ctype in changes:
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

def getErrors(l):
	errors = defaultdict(list)
	cnt = Counter(l)
	dict_en = Dict("en_US")
	for el, c in cnt.items():
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
		for ch in "?!,.()":
			if ch in el:
				errors["unused_signs"].append(el)
				break
		for w in el.split():
			if not dict_en.check(w):
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
