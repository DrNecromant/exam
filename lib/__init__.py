from getpass import getuser
from sys import platform
from storage import Storage
from xls import XLS
from db import DB

dbname = "translate.db"
testname = "test.xls"

def getDropboxPath():
	if platform == "linux2":
		return "/home/%s/Dropbox/" % getuser()
	elif platform == "darwin":
		return "/Users/%s/Dropbox/" % getuser()
	else:
		raise Exception("Unsupported OS %s" % sys.platform)
