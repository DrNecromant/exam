def printWords(words):
	if not words:
		print "Could not find"
		return
	for eng, rus, fname in words:
		print "%s | %s" % (eng.encode("utf8"), rus.encode("utf8"))
		print "\t%s" % fname
