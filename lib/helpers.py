def printWords(words):
	if not words:
		print "Could not find"
		return
	for eng, rus, fname in words:
		print "%s | %s" % (eng.encode("utf8"), rus.encode("utf8"))
		print "\t%s" % fname

def printStats(stats):
	for stat in stats:
		print "========== %s ==========" % stat
		stat_dict = dict(stats[stat])
		keys = sorted(stat_dict.keys())
		zero_key = 0
		if zero_key in keys:
			keys.remove(zero_key)
		half = len(keys)/2
		small_keys = keys[:half]
		big_keys = keys[half:]
		zero_sum = stat_dict.get(0, 0)
		small_sum = sum([stat_dict[k] for k in small_keys if k in small_keys])
		big_sum = sum([stat_dict[k] for k in big_keys if k in big_keys])
		total = float(zero_sum + small_sum + big_sum)
		print "0: %s (%.2f%%)" % (zero_sum, 100 * (zero_sum/total))
		print "%s-%s: %s (%.2f%%)" % (small_keys[0], small_keys[-1], small_sum, 100 * (small_sum/total))
		print "%s-%s: %s (%.2f%%)" % (big_keys[0], big_keys[-1], big_sum, 100 * (big_sum/total))
