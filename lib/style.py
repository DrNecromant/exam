import types

DONOT_PRINT_FUNC_NAME = (
	"__init__",
	"getFileSha",
	"getWordEntries",
	"getWords",
	"getShortPath",
	"getFullPath",
	"getSha",
	"loadData",
	"addWord",
	"createWord",
	"changeWord",
	"updateWord",
	"updateFileSha",
	"removeWord",
	"deleteWord",
	"changeSha",
	"getDictEngWord",
	"checkEngWord",
	"getBlankChanges",
	"mkClone",
	"commit",
	"applyChanges",
	"addEngWord",
	"createDictEngWord",
	"getChanges",
	"getFile",
	"updateCounter",
	"changeCounter",
	"dumpData",
	"mkFile",
	"saveTestWords",
	"getHistoryByDate",
	"getRawDataByDate",
	"getMinDate",
	"getMaxDate",
	"getMinMaxDates",
	"getFiles",
	"unlinkFiles",
)

class DecoMeta(type):
	def __new__(cls, name, bases, attrs):
		cls.__name = name
		for attr_name, attr_value in attrs.iteritems():
			if isinstance(attr_value, types.FunctionType):
				attrs[attr_name] = cls.deco(attr_value)
		return super(DecoMeta, cls).__new__(cls, name, bases, attrs)

	@classmethod
	def deco(cls, func):
		convert_list = lambda p: "%s: %s" %(type(p), len(p)) if type(p) in (list, tuple) and len(p) > 3 else p
		class_name = cls.__name
		func_name = func.__name__
		def wrapper(*args, **kwargs):
			if not func_name in DONOT_PRINT_FUNC_NAME:
				args_to_print = args[1:]
				kwargs_to_print = kwargs.items()
				print "# %s::%s" % (class_name, func_name)
				if args_to_print:
					for item in args_to_print:
						print "\t*  %s" % convert_list(item)
				if kwargs_to_print:
					for items in kwargs_to_print:
						print "\t** %s: %s" % (items[0], convert_list(items[1]))
			return func(*args, **kwargs)
		return wrapper
