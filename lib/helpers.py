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
	if len(l) < c * 3:
		shuffle(l)
		return l[:c]
	l = l[:c] + sample(l[c:], c)
	i = c / 4
	l = l[:i] + sample(l[i:], c - i)
	shuffle(l)
	return l

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
