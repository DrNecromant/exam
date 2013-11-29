from os import path, walk
import hashlib
import tempfile
import shutil

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
				if [e for e in exceptions if f.startswith(e)]:
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

	def mkfile(self, prifix = "", suffix = "", dir = ""):
		name = tempfile.mktemp(prefix = prifix, suffix = suffix, dir = self.getFullPath(dir))
		return name

	def mkClone(self, fpath, prefix = "", suffix = "_clone"):
		dir, fullname = fpath.split()
		name, ext = path.splitext(fullname)
		new_fpath = path.join(dir, prefix + name + suffix + ext)
		shutil.copy(self.getFullPath(fpath), self.getFullPath(new_fpath))
