import sqlite3

class DB():
	def __init__(self, dbpath):
		self.p = dbpath
		self.con = sqlite3.connect(self.p)
		self.cur = self.con.cursor()
		self.blank_changes = {"create": list(), "update": list(), "delete": list()}
		self.changes = {"create": list(), "update": list(), "delete": list()}
		self.cur.executescript("PRAGMA foreign_keys=ON;" + \
			"CREATE TABLE IF NOT EXISTS file(id INTEGER PRIMARY KEY, name STRING, sha STRING DEFAULT 'nosha');" + \
			"CREATE TABLE IF NOT EXISTS word(id INTEGER PRIMARY KEY, eng STRING, " + \
				"rus STRING, file INTEGER, count INTEGER DEFAULT 0, " + \
				"success INTEGER DEFAULT 0, FOREIGN KEY(file) REFERENCES file(id));")
		self.con.commit()

	def getErrors(self):
		errors = dict()
		duplicates = self.cur.execute("SELECT eng from word group by eng having count(rus) > 1").fetchall()
		if duplicates:
			errors["duplicates"] = map(lambda a: a[0], duplicates)
		spaces = self.cur.execute("SELECT eng from word where eng like ' %' or eng like '% ' or eng like '%  %'").fetchall()
		if spaces:
			errors["spaces"] = map(lambda a: a[0], spaces)
		articles = self.cur.execute("SELECT eng from word where eng like 'a %' or eng like 'the %'").fetchall()
		if articles:
			errors["articles"] = map(lambda a: a[0], articles)
		engs = self.cur.execute("SELECT eng from word").fetchall()
		rus_letters = [s[0] for s in engs if not all(ord(c) < 128 for c in s[0])]
		if rus_letters:
			errors["rus_letters"] = rus_letters
		signs = [s[0] for s in engs if "?" in s[0] or "!" in s[0] or "." in s[0] or "," in s[0] or "(" in s[0] or ")" in s[0]]
		if signs:
			errors["unused_signs"] = signs
		return errors

	def quit(self):
		self.con.close()

	def commit(self):
		if self.changes == self.blank_changes:
			print "There is nothing to commit"
			return
			
		for ctype in self.changes:
			print "========== %s ===========" % ctype
			for c in self.changes[ctype]:
				print "==> %s" % c

		answer = raw_input("Want to apply database changes? y/(n)? ")
		if not answer:
			self.con.rollback()
		else:
			print "Apply database changes"
			self.con.commit()
			self.changes = {"create": list(), "update": list(), "delete": list()}

	def getAllFiles(self):
		files = self.cur.execute("SELECT name from file").fetchall()
		if files:
			files = map(lambda a: a[0], files)
		return files

	def findWords(self, word):
		return self.cur.execute("SELECT eng, rus, file.name from word " + \
			"left join file on word.file = file.id " + \
			"where eng like ?", ("%" + word + "%",)).fetchall()

	def getWords(self, word):
		return self.cur.execute("SELECT eng, rus, file.name from word " + \
			"left join file on word.file = file.id " + \
			"where eng=?", (word,)).fetchall()

	def getAllWords(self):
		return self.cur.execute("SELECT eng, rus, file.name from word " + \
			"left join file on word.file = file.id order by success / cast(count as real)").fetchall()

	def updateCounter(self, eng, counter):
		count = self.cur.execute("SELECT %s FROM word WHERE eng=?" % counter, (eng,)).fetchone()[0]
		count += 1
		self.cur.execute("UPDATE word SET %s=? WHERE eng=?" % counter, (count, eng))
		self.changes["update"].append("%s %s %s" % (eng, counter, count))

	def getSha(self, name):
		sha = self.cur.execute("SELECT sha FROM file WHERE name = ?", (name,)).fetchone()[0]
		return sha

	def updateSha(self, fname, sha):
		self.changes["update"].append("%s | %s" % (fname, sha))
		self.cur.execute("UPDATE file SET sha=? WHERE name=?", (sha, fname))

	def loadData(self, name):
		data = self.cur.execute("SELECT eng, rus FROM word LEFT JOIN file ON file.id = word.file WHERE file.name = ?", (name,)).fetchall()
		return data

	def deleteFile(self, fname):
		self.changes["delete"].append(fname)
		self.cur.execute("SELECT id FROM file WHERE name=?", (fname,))
		file_id = self.cur.fetchone()[0]
		self.cur.execute("DELETE FROM word WHERE file=?", (file_id,))
		self.cur.execute("DELETE FROM file WHERE name=?", (fname,))

	def createFile(self, fname, sha, words):
		self.changes["create"].append("%s | %s" % (fname, sha))
		self.cur.execute("INSERT INTO file(name, sha) VALUES(?, ?)", (fname, sha))
		for word in words:
			eng, rus = word
			self.createWord(fname, eng, rus)

	def deleteWord(self, fname, eng):
		self.changes["delete"].append("%s | %s" % (fname, eng))
		self.cur.execute("SELECT id FROM file WHERE name=?", (fname,))
		file_id = self.cur.fetchone()[0]
		self.cur.execute("DELETE FROM word WHERE eng=? AND file=?", (eng, file_id))

	def createWord(self, fname, eng, rus):
		self.changes["create"].append("%s | %s | %s" % (fname, eng, rus))
		self.cur.execute("SELECT id FROM file WHERE name=?", (fname,))
		file_id = self.cur.fetchone()[0]
		self.cur.execute("INSERT INTO word(eng, rus, file) VALUES(?, ?, ?)", (eng, rus, file_id))

	def updateWord(self, fname, eng, rus1, rus2):
		self.changes["update"].append("%s | %s | %s -> %s" % (fname, eng, rus1, rus2))
		self.cur.execute("SELECT id FROM file WHERE name=?", (fname,))
		file_id = self.cur.fetchone()[0]
		self.cur.execute("UPDATE word SET rus=? WHERE file=? AND eng=?", (rus2, file_id, eng))

	def getStats(self):
		table = self.cur.execute("SELECT eng, count, success, name FROM word join file on word.file = file.id").fetchall()
		result_table = [["eng", "count", "success", "file", "source", "type"]]
		for row in table:
			row = list(row)
			row.append(row[3].split("/")[1])
			if " " in row[0]:
				row.append("complex")
			else:
				row.append("single")
			result_table.append(row)
		return result_table
