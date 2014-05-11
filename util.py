from _exam_lib import Exam, parser

parser.add_option("--find", "-f", dest = "find",
	help = "find word or part of word")
parser.add_option("--sync", "-s", action = "store_true",
	dest = "sync", help = "sync")
parser.add_option("--join", "-j", action = "store_true",
	dest = "join", help = "join")
parser.add_option("--plot", "-p", action = "store_true",
	dest = "plot", help = "plot")

tool = Exam()
options = tool.options
if options.find:
	tool.processDBWord(options.find)
if options.sync:
	tool.sync()
	tool.processDBErrors()
if options.join:
	tool.joinTestFiles()
if options.plot:
	stats = tool.getStats()
	tool.buildPlot(stats)
