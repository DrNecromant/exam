from os import path, walk, unlink
from shutil import copy2
import hashlib
import tempfile
from style import *

class Storage():
	__metaclass__ = DecoMeta
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

	def getFiles(self, subdir = None, fext = None):
		result = list()
		fullpath = self.getFullPath(subdir)
		for p, dirs, files in walk(fullpath):
			for f in files:
				if fext and not f.endswith(fext):
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

	def mkFile(self, prifix = "", suffix = "", subdir = ""):
		fpath = tempfile.mktemp(prefix = prifix, suffix = suffix, dir = self.getFullPath(subdir))
		return fpath

	def unlinkFiles(self, files):
		for f in files:
			unlink(f)

	def getFile(self, name, subdir = ""):
		if subdir:
			name = path.join(subdir, name)
		fpath = self.getFullPath(name)
		return fpath

	def mkClone(self, fpath, prefix = "", suffix = "_clone"):
		dir, fullname = path.split(fpath)
		name, ext = path.splitext(fullname)
		new_fpath = path.join(dir, prefix + name + suffix + ext)
		src = self.getFullPath(fpath)
		dst = self.getFullPath(new_fpath)
		if path.exists(dst):
			unlink(dst)
		copy2(src, dst)
