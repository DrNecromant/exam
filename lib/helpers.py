def printFiles(data):
	print "files %s, words %s" % (data["files"], data["words"])
	for id, name, size in data["filelist"]:
		print "%s) %s %s" % (id, name, size)
