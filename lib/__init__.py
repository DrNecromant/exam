from getpass import getuser
from sys import platform
from storage import Storage
from xls import XLS
from db import DB
from style import *
from consts import *
import helpers as h
import config

def getDropboxPath():
	if platform == "linux2":
		return "/home/%s/Dropbox/" % getuser()
	elif platform == "darwin":
		return "/Users/%s/Dropbox/" % getuser()
	else:
		raise Exception("Unsupported OS %s" % sys.platform)
