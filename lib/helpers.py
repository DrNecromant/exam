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
	x = c / 3
	y = c * 3
	z = c - x * 2
	res = l[:x] + sample(l[x:y], x) + sample(l[y:], z)
	shuffle(res)
	return res

def shuffleList(l):
	shuffle(l)
	return l

def getStatsFromRawData(data):
	part = 10000
	p_sum = f_sum = idle = good = bad = 0
	for passed, failed in data:
		p_sum += passed
		f_sum += failed
		if passed == 0 and failed == 0:
			idle += 1
		elif passed > failed:
			good += 1
		else:
			bad += 1
	base = (good + bad + idle)
	if good + bad != 0:
		good = part * good / base
		bad = part * bad / base
	idle = part - good - bad
	return [p_sum, f_sum, idle, good, bad]

def buildPlot(files, **stats):
	plt.figure("quantuty")
	plt.plot(stats["p_sum"], color = "g", linewidth = 2)
	plt.plot(stats["f_sum"], color = "r", linewidth = 2)
	plt.savefig(files[0])
	plt.figure("quality")
	plt.plot(stats["idle"], color = "b", linewidth = 2)
	plt.plot(stats["good"], color = "g", linewidth = 2)
	plt.plot(stats["bad"], color = "r", linewidth = 2)
	plt.savefig(files[1])
