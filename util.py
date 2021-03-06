from _exam_lib import Exam, parser

parser.add_option("--find", "-f", dest = "find",
	help = "find word or part of word")
parser.add_option("--sync", "-s", action = "store_true",
	dest = "sync", help = "sync")
parser.add_option("--plot", "-p", action = "store_true",
	dest = "plot", help = "plot")
parser.add_option("--today", "-t", action = "store_true",
	dest = "today", help = "today")

tool = Exam()
options = tool.options
if options.find:
	tool.processDBWord(options.find)
if options.sync:
	tool.sync()
	tool.processDBErrors()
if options.plot:
	stats = tool.getStats()
	tool.buildPlot(stats)
if options.today:
	count = tool.processWordCount()
