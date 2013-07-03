from os import walk, path
import hashlib

class Storage():
	def __init__(self, storage_path):
		self.path = storage_path

	def getFullPath(self, shortpath = None):
		if not shortpath:
			return self.path
		return path.join(self.path, shortpath)

	def getShortPath(self, fullpath = None):
		if fullpath and fullpath.startswith(self.path):
			return fullpath.replace(self.path, "")
		return None

	def getFiles(self, subdir = None, fext = None, exceptions = None):
		result = list()
		fullpath = self.getFullPath(subdir)
		for p, dirs, files in walk(fullpath):
			for f in files:
				if fext and not f.endswith(fext):
					continue
				if f in exceptions:
					continue
				result.append(path.join(p, f))
		return result

	def getSha(self, filename, blocksize = 65536):
		filepath = self.getFullPath(filename)
		hasher = hashlib.md5()
		fd = open(filepath)
		buf = fd.read(blocksize)
		while buf:
			hasher.update(buf)
			buf = fd.read(blocksize)
		fd.close()
		return hasher.hexdigest()
