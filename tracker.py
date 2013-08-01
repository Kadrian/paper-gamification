import os
import sys
import time
import operator
import logging

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from watchdog.events import FileModifiedEvent

class GamificationHandler(FileSystemEventHandler):
	
	def __init__(self, filename):
		FileSystemEventHandler.__init__(self)

		self.filename = filename
		self.stats = {}
		# words = {"hello": 5, "no": 3}
		self.words = {}

	def on_modified(self, event):
		if type(event) == FileModifiedEvent:
			if os.path.abspath(self.filename) == event.src_path:
				self.register_change()
				self.do_gamification()

	def register_change(self):
		f = open(self.filename)

		avg_len = 0
		num_words = 0

		for line in f.readlines():
			word_split = line.split(" ")
			for w in word_split:
				if w.strip() != "" and w.isalnum():
					word = w.strip().lower()
					# Determine average word length
					if avg_len == 0:
						avg_len = len(word)
					else:	
						avg_len += len(word)
						avg_len /= 2.0
					# Count distinct words with occurrences
					if word not in self.words:
						self.words[word] = 0
					self.words[word] += 1
					# Count all words
					num_words += 1

		# Determine Oxford coverage
		oxford_coverage = self.get_coverage("./oxford.txt")

		# Determine Fancy word coverage
		fancy_coverage = self.get_coverage("./fancy.txt")

		self.stats = {
			"num_words" : num_words,
			"different_words" : len(self.words),
			"avg_len" : avg_len,
			"oxford_coverage" : {
				"total" : oxford_coverage["total"],
				"num_hits": len(oxford_coverage["hits"])
			},
			"fancy_coverage" : {
				"total" : fancy_coverage["total"],
				"num_hits": len(fancy_coverage["hits"])
			}
		}

		# Sort
		#stats = sorted(words.iteritems(), key=operator.itemgetter(1), reverse=True)		

		# Output
		# top = 50
		# for word, num in stats:
		# 	if top <= 0:
		# 		break
		# 	print word + " : " + str(num)
		# 	top -= 1

		logging.info("Stats: " + str(self.stats))


	def get_coverage(self, filename):
		""" Reads a list of words and compares it to the own words"""
		words = []
		num_words = 0
		# Count	and compare
		f = open(filename)
		for word in f.readlines():
			if word.strip() != "":
				words.append(word.strip().lower())
				num_words += 1
			
		hits = set(words).intersection(set(self.words.keys()))
		return { "total": num_words, "hits": list(hits)}


	def do_gamification(self):
		pass


if __name__ == "__main__":

	history_file = "history"
	logging.basicConfig(level=logging.INFO,
						format='%(asctime)s - %(message)s',
						datefmt='%Y-%m-%d %H:%M:%S')
	if len(sys.argv) != 2:
		print "Please supply a file to be watched"
		sys.exit()

	filename = sys.argv[1]
	path = os.path.dirname(os.path.abspath(filename))

	# Observer setup + start
	event_handler = GamificationHandler(filename)
	observer = Observer()
	observer.schedule(event_handler, path=path, recursive=True)
	observer.start()
	try:
		while True:
			time.sleep(1)
	except KeyboardInterrupt:
		observer.stop()
	observer.join()