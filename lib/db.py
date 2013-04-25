import sqlite3

class DB():
	def __init__(self, dbpath):
		self.p = dbpath
		print "Connect to database %s" % self.p
		self.con = sqlite3.connect(self.p)
		self.cur = self.con.cursor()
		self.changes = self._blank_changes()

	def quit(self):
		print "Close database connection"
		self.con.close()

	def _blank_changes(self):
		return {
            "create": list(),
            "update": list(),
            "delete": list(),
        }

	def _is_blank_changes(self):
		for ctype in self.changes:
			if self.changes[ctype]:
				return False
		return True

	def _apply_changes(self):
		for ctype in self.changes:
			if not self.changes[ctype]:
				continue
			print "========== %s ===========" % ctype
			for c in self.changes[ctype]:
				print "==> %s" % c

		answer = raw_input("Want to apply database changes? y/(n)? ")
		if not answer:
			self.con.rollback()
		else:
			print "Apply database changes"
			self.con.commit()
			self.changes = self._blank_changes()

	def printFileList(self, files = None):
		if not files:
			files = map(lambda a: a[0], self.cur.execute("SELECT id FROM file").fetchall())
			file_count = self.cur.execute("SELECT count(*) from file").fetchone()[0]
			word_count = self.cur.execute("SELECT count(*) FROM word").fetchone()[0]
		else:
			file_count = len(files)
			word_count = self.cur.execute("SELECT count(*) FROM word WHERE file in (%s)" % ", ".join(["?"] * len(files)), files).fetchone()[0]

		print "files %s, words %s" % (file_count, word_count)
		for fileid in files:
			word_count = self.cur.execute("SELECT count(*) FROM word WHERE file=?", (fileid,)).fetchone()[0]
			fname = self.cur.execute("SELECT name FROM file WHERE id=?", (fileid,)).fetchone()[0]
			print "%s) %s %s" % (fileid, fname, word_count)

	def getWord(self, word):
		return self.cur.execute("SELECT eng, rus, file.name from word " + \
			"left join file on word.file = file.id " + \
			"where eng like ?", ("%" + word + "%",)).fetchall()

	def getValues(self, files = None):
		if not files:
			return self.cur.execute("SELECT eng, rus, file.name from word " + \
				"left join file on word.file = file.id").fetchall()
		return self.cur.execute("SELECT eng, rus, file.name from word " + \
			"left join file on word.file = file.id " + \
			"where file in (%s)" % ", ".join(["?"] * len(files)), files).fetchall()

	def sync(self, values):
		self.cur.executescript("PRAGMA foreign_keys=ON;" + \
			"CREATE TABLE IF NOT EXISTS file(id INTEGER PRIMARY KEY, name STRING);" + \
			"CREATE TABLE IF NOT EXISTS word(id INTEGER PRIMARY KEY, eng STRING, " + \
				"rus STRING, file INTEGER, count INTEGER DEFAULT 0, " + \
				"success INTEGER DEFAULT 0, FOREIGN KEY(file) REFERENCES file(id));")
	
		for eng, rus, filename in values:
			self.cur.execute("SELECT id FROM file WHERE name=?", (filename,))
			fileid = self.cur.fetchone()
			if not fileid:
				self.cur.execute("INSERT INTO file(name) VALUES(?)", (filename,))
				self.cur.execute("SELECT id FROM file WHERE name=?", (filename,))
				fileid = self.cur.fetchone()
				self.changes["create"].append("%s %s" % (fileid[0], filename))
			fileid = fileid[0]
			self.cur.execute("SELECT rus FROM word WHERE file=? and eng=?", (fileid, eng))
			word = self.cur.fetchone()
			if not word:
				self.cur.execute("INSERT INTO word(eng, rus, file) VALUES(?, ?, ?)", (eng, rus, fileid))
				self.changes["create"].append("%s | %s" % (eng, fileid))
			elif word[0] != rus:
				self.cur.execute("UPDATE word SET rus=? WHERE file=? and eng=?", (rus, fileid, eng))
				self.changes["update"].append("%s | %s" % (eng, fileid))

		engs, russ, files = zip(*values)
		base_engs = map(lambda a: a[0], self.cur.execute("SELECT eng FROM word").fetchall())
		for base_eng in base_engs:
			if not base_eng in engs:
				self.cur.execute("DELETE FROM word WHERE eng=?", (base_eng,))
				self.changes["delete"].append("%s" % base_eng)

		files = list(set(files))
		base_files = map(lambda a: a[0], self.cur.execute("SELECT name from file").fetchall())
		for base_file in base_files:
			if not base_file in files:
				print files
				print base_file
				self.cur.execute("DELETE FROM file WHERE name=?", (base_file,))
				self.changes["delete"].append("%s" % base_file)

		if not self._is_blank_changes():
			self._apply_changes()
		else:
			print "There is nothing to sync"
