from random import sample, shuffle

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
	res = [p_sum, f_sum, total]
	for key in range(max_passed + 1):
		if key in stat_dict:
			res.append(stat_dict[key])
		else:
			res.append(0)
	print res
	return res

def buildPlot(file_to_save, stats):
	plt.figure(file_to_save)
	for stat in stats:
		plt.plot(stat)
	plt.savefig(file_to_save)
