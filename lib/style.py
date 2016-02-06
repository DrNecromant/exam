import config
import re
from pprint import pprint
from collections import defaultdict

class DecoMeta(type):
	def __new__(cls, name, bases, attrs):
		cls.__name = name
		if name == "_base_DB":
			cls.db_changes = defaultdict(int)
		for attr_name, attr_value in attrs.iteritems():
			if callable(attr_value):
				attrs[attr_name] = cls.deco(attr_value)
		return type.__new__(cls, name, bases, attrs)

	@classmethod
	def deco(cls, func):
		convert_list = lambda p: "%s: %s" %(type(p), len(p)) if type(p) in (list, tuple) and len(p) > 3 else p
		class_name = cls.__name
		func_name = func.__name__
		def wrapper(*args, **kwargs):
			if config.debug:
				args_to_print = args[1:]
				kwargs_to_print = kwargs.items()
				print "# %s::%s" % (class_name, func_name)
				if args_to_print:
					for item in args_to_print:
						print "\t*  %s" % convert_list(item)
				if kwargs_to_print:
					for items in kwargs_to_print:
						print "\t** %s: %s" % (items[0], convert_list(items[1]))
			if class_name == "_base_DB":
				if re.match("create|delete|update", func_name):
					cls.db_changes[func_name] += 1
				if func_name in ("commit", "rollback"):
					pprint(dict(cls.db_changes))
					cls.db_changes = defaultdict(int)
			return func(*args, **kwargs)
		return wrapper
