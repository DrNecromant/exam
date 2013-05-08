def printFiles(data):
	print "files %s, words %s" % (data["files"], data["words"])
	for id, name, size in data["filelist"]:
		print "%s) %s %s" % (id, name, size)

def printValues(data):
	if not data:
		print "Could not find"
		return
	for eng, rus, fname in data:
		print "%s" % eng.encode("utf8")
		print "\t%s" % rus.encode("utf8")
		print "\t%s" % fname.encode("utf8")
