from _exam_lib import Exam, parser

parser.add_option("--rus", "-r", action="store_true",
	dest="rus", help="exam rus words")
parser.add_option("--count", "-c", dest="count",
	default = 20, type = "int", help="number of word to exam")

exam = Exam()
options = exam.options
exam.sync()
if exam.processDBErrors():
	exam.doExam(options.count, options.rus)
