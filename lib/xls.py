from xlrd import open_workbook
from xlwt import Workbook
from style import *

class XLS():
	__metaclass__ = DecoMeta
	def __init__(self):
		pass

	def dumpData(self, dst, words, column_num = 2):
		wb = Workbook()
		ws = wb.add_sheet("test")
		row = 0
		max_lens = [0] * column_num
		for w in words:
			for i in range (column_num):
				l = len(w[i])
				if l > max_lens[i]:
					max_lens[i] = l
				ws.write(row, i, w[i]) 
			row += 1
		for i in range (column_num):
			ws.col(i).width = max_lens[i] * 256
		wb.save(dst)

	def loadData(self, filename, column_num = 2):
		sheet = open_workbook(filename).sheet_by_index(0)
		return [tuple(sheet.row_values(rownum)[:column_num]) for rownum in range(sheet.nrows)]
