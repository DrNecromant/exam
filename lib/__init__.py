from getpass import getuser
from sys import platform
from storage import Storage
from xls import XLS
from db import DB
from lingvo import Lingvo
from style import *
from consts import *
import helpers as h
import config

def getCloudPath():
	if platform == "linux2":
		return "/home/%s/Google Drive/" % getuser()
	elif platform == "darwin":
		return "/Users/%s/Google Drive/" % getuser()
	else:
		raise Exception("Unsupported OS %s" % sys.platform)
