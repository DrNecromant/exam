import urllib2
import sys
import re
from consts import LINGVO_URL
from helpers import unescape

class LingvoError(Exception):
	pass

class Lingvo():
	def __init__(self, entry):
		self.entry = entry
		self.html = self.getContent()
		self.translations = None
		self.examples = None
		self.phrases = None
		self.ex_list = None
		if self.html:
			self.__calc__()

	def __getCount__(self, param):
		m = re.search(".*%s\s*\((\d+)\).*" % param, self.html)
		if not m:
			return None
		return int(m.group(1))

	def __calc__(self):
		self.translations = self.__getCount__("Translations")
		self.examples = self.__getCount__("Examples from texts")
		self.phrases = self.__getCount__("Phrases")
		self.ex_list = self.getExamples()

	def _tunePhrase(self, phrase):
		new_phrase = unescape(phrase.decode("utf-8"))
		new_phrase = re.sub("<.*?em.*?>", "", new_phrase)
		return new_phrase

	def getContent(self):
		try:
			url = LINGVO_URL % urllib2.quote(self.entry.decode("utf8"))
			response = urllib2.urlopen(url)
			html = response.read()
		except urllib2.URLError, e:
			html = None
		return html

	def getExamples(self):
		examples = list()
		if not self.html or not self.examples:
			return examples

		ex_html_modified = self.html.replace("\n", "").replace("\r", "").replace("\t", "")
		div = "<div.+?>(.+?)</div>"
		td_class = "l-examples__tdExamp"

		phrases = re.findall("%s orig.+?%s.+?%s transl.+?%s" % (td_class, div, td_class, div), ex_html_modified)
		for phrase_pair in phrases:
			examples.append(map(self._tunePhrase, phrase_pair))

		return examples

if __name__ == "__main__":
	l = Lingvo("world")
	print l.translations, l.examples, l.phrases
	examples = l.getExamples()
	if not examples:
		print "no examples"
	else:
		for e in examples[0]:
			print e
