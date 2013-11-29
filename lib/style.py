import types

class DecoMeta(type):
	def __new__(cls, name, bases, attrs):
		for attr_name, attr_value in attrs.iteritems():
			if isinstance(attr_value, types.FunctionType):
				attrs[attr_name] = cls.deco(name, attr_value)
		return super(DecoMeta, cls).__new__(cls, name, bases, attrs)

	@classmethod
	def deco(cls, name, func):
		class_name = name
		func_name = func.__name__
		def wrapper(*args, **kwargs):
			print "# %s:%s ..." % (class_name, func_name)
			func(*args, **kwargs)
		return wrapper
