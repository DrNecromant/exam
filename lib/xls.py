from xlrd import open_workbook
from xlwt import Workbook
from style import *

class XLS():
	__metaclass__ = DecoMeta
	def __init__(self):
		pass

	def dumpData(self, dst, words):
		wb = Workbook()
		ws = wb.add_sheet("test")
		row = 0
		for w in words:
			ws.write(row, 0, w[0]) 
			ws.write(row, 1, w[1]) 
			row += 1
		wb.save(dst)

	def loadData(self, filename):
		sheet = open_workbook(filename).sheet_by_index(0)
		return [tuple(sheet.row_values(rownum)[:2]) for rownum in range(sheet.nrows)]
