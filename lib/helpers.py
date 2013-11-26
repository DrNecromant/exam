from random import sample, shuffle
import types

class DecoMeta(type):
	def __new__(cls, name, bases, attrs):
		for attr_name, attr_value in attrs.iteritems():
			if isinstance(attr_value, types.FunctionType):
				attrs[attr_name] = cls.deco(attr_value)
		return super(DecoMeta, cls).__new__(cls, name, bases, attrs)

	@classmethod
	def deco(cls, func):
		def wrapper(*args, **kwargs):
			print "%s..." % func.__name__
			func(*args, **kwargs)
		return wrapper

def printWords(words):
	if not words:
		print "Could not find"
		return
	for eng, rus, fname in words:
		print "%s | %s" % (eng.encode("utf8"), rus.encode("utf8"))
		print "\t%s" % fname

def printErrors(errors, mapper):
	for error_type in errors:
		print "========== ERROR %s ==========" % error_type
		for eng in errors[error_type]:
			printWords(mapper(eng))

def printChanges(changes):
	for ctype in changes:
		print "========== %s ===========" % ctype
		for c in changes[ctype]:
			print "==> %s" % c

def smartSelection(l, c):
	l = l[:c] + sample(l[c:], c)
	i = c / 4
	l = l[:i] + sample(l[i:], c - i)
	shuffle(l)
	return l
