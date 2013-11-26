from optparse import OptionParser

from _exam_lib import Exam

parser = OptionParser()
parser.add_option("--find", "-f", dest = "find",
	help = "find word or part of word")
parser.add_option("--sync", "-s", action = "store_true",
	dest = "sync", help = "sync")
parser.add_option("--stats", "-t", action = "store_true",
	dest = "stats", help = "stats")

(options, args) = parser.parse_args()

tool = Exam()
if options.find:
	tool.processDBWord(options.find)
if options.sync:
	tool.sync()
	tool.processDBErrors()
if options.stats:
	tool.saveStats()
