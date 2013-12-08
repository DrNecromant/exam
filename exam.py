from optparse import OptionParser

from _exam_lib import Exam

parser = OptionParser()
parser.add_option("--rus", "-r", action="store_true",
	dest="rus", help="exam rus words")
parser.add_option("--fake", "-f", action="store_true",
	dest="fake", help="dry run")
parser.add_option("--count", "-c", dest="count",
	default = 20, type = "int", help="number of word to exam")

(options, args) = parser.parse_args()

exam = Exam(fake = options.fake)
exam.sync()
if exam.processDBErrors():
	exam.doExam(options.count, options.rus)
