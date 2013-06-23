import hashlib

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

def getSha(filename, blocksize = 65536):
	hasher = hashlib.md5()
	fd = open(filename)
	buf = fd.read(blocksize)
	while buf:
		hasher.update(buf)
		buf = fd.read(blocksize)
	fd.close()
	return hasher.hexdigest()
