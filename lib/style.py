import types

DONOT_PRINT_FUNC_NAME = (
	"__init__",
	"getFullPath",
	"getSha",
	"getShortPath",
	"getBlankChanges",
	"updateCounter",
	"createWord",
	"updateWord",
	"deleteWord",
	"getDateNow"
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
		class_name = cls.__name
		func_name = func.__name__
		def wrapper(*args, **kwargs):
			if not func_name in DONOT_PRINT_FUNC_NAME:
				print "# %s:%s ..." % (class_name, func_name)
			return func(*args, **kwargs)
		return wrapper
