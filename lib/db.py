from _base_db import _base_DB

class DB(_base_DB):
	def __init__(self, dbpath):
		_base_DB.__init__(self, dbpath)
