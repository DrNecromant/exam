from _exam_lib import Exam, parser

parser.add_option("--count", "-c", dest="count",
	default = 20, type = "int", help="number of word to exam")
parser.add_option("--phrase", "-p", action = "store_true",
	dest = "phrase", help = "test phrases")

exam = Exam()
options = exam.options
exam.sync()
if exam.processDBErrors():
	if options.phrase:
		exam.doExam(options.count, phrase = True)
	else:
		exam.doExam(options.count)
