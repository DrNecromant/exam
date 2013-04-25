from xlrd import open_workbook
from xlwt import Workbook

class XLS():
	def __init__(self):
		pass

	def dump(self, dst, values):
		wb = Workbook()
		ws = wb.add_sheet("test")
		row = 0
		for v in values:
			ws.write(row, 0, v[0]) 
			ws.write(row, 1, v[1]) 
			row += 1
		wb.save(dst)

	def load(self, files):
		data = lambda f, s, r: [s.cell(r, 0).value, s.cell(r, 1).value, f]
		sheets = lambda f: open_workbook(f).sheets()
		values = [data(fname, sheet, row) \
			for fname in files \
			for sheet in sheets(fname) \
			for row in range(sheet.nrows)]
		return values
