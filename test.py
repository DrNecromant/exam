class e1(Exception):
	pass

class e2(Exception):
	pass

def f():
	try:
		a = a
	except Exception, e:
		raise e2("How")

try:
	f()
except (e1, e2), e:
	print dir(e)
	print str(e)
