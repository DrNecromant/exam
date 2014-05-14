from _exam_lib import Exam, parser

parser.add_option("--time", "-t", dest = "time",
	default = 60, type = "int", help = "delay between getting words")

sync = Exam()
options = sync.options
sync.processLingvoWords(delay = options.time)
