import urllib2
import sys
import re
from consts import IN_URL_TEMP, EX_URL_TEMP
from helpers import unescape

class Lingvo():
	def __init__(self, entry):
		self.entry = entry
		self.translations = None
		self.examples = None
		self.phrases = None
		self.__calc__()

	def __getCount__(self, html, param):
		m = re.search(".*%s\s*\((\d+)\).*" % param, html)
		f = open("l.txt", "w")
		print >>f, param
		print >>f, html
		f.close()
		return int(m.group(1))

	def __calc__(self):
		try:
			url = IN_URL_TEMP % urllib2.quote(self.entry.decode("utf8"))
			response = urllib2.urlopen(url)
			in_html = response.read()
			self.translations = self.__getCount__(in_html, "Translations")
			self.examples = self.__getCount__(in_html, "Examples")
			self.phrases = self.__getCount__(in_html, "Phrases")
		except urllib2.URLError, e:
			self.translations = None
			self.examples = None
			self.phrases = None

	def _tunePhrase(self, phrase):
		new_phrase = unescape(phrase.decode("utf-8"))
		new_phrase = re.sub("<.*?em.*?>", "", new_phrase)
		return new_phrase

	def getExamples(self):
		examples = list()
		if not self.examples:
			return examples

		try:
			url = EX_URL_TEMP % urllib2.quote(self.entry.decode("utf8"))
			response = urllib2.urlopen(url)
			ex_html = response.read()
		except urllib2.URLError, e:
			return examples

		ex_html_modified = ex_html.replace("\n", "").replace("\r", "").replace("\t", "")
		div = "<div.+?>(.+?)</div>"
		td_class = "l-examples__tdExamp"

		phrases = re.findall("%s orig.+?%s.+?%s transl.+?%s" % (td_class, div, td_class, div), ex_html_modified)
		for phrase_pair in phrases:
			examples.append(map(self._tunePhrase, phrase_pair))

		return examples

	def getRank(self):
		if self.examples is None:
			return None
		return self.translations + self.examples + self.phrases

if __name__ == "__main__":
	l = Lingvo("my world")
	print l.translations, l.examples, l.phrases
	examples = l.getExamples()
	if not examples:
		print "no examples"
	else:
		for e in examples[0]:
			print e
