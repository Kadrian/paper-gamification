import os
import sys
import time
import operator
import logging
import requests
import json

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from watchdog.events import FileModifiedEvent


class GamificationHandler(FileSystemEventHandler):
	
	def __init__(self, paper_filename, publish_url, paper_id):

		FileSystemEventHandler.__init__(self)

		self.paper_filename = paper_filename 
		self.publish_url = publish_url 
		self.paper_id = paper_id

		self.stats = {}
		# words = {"hello": 5, "no": 3}
		self.words = {}

	def on_modified(self, event):
		if type(event) == FileModifiedEvent:
			if os.path.abspath(self.paper_filename) == event.src_path:
				self.calculate_statistics()
				self.publish()

	def calculate_statistics(self):
		f = open(self.paper_filename)

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
		f.close()

		# Determine Oxford coverage
		oxford_coverage = self.get_coverage("./oxford.txt")

		# Determine Fancy word coverage
		fancy_coverage = self.get_coverage("./fancy.txt")

		# Determine academic word list coverage 
		awl_coverage = self.get_awl_coverage("./awl.txt")

		# Build stats together
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
			},
			"awl_coverage" : {
				"words_total": awl_coverage["words_total"],
				"words_hits": awl_coverage["words_hits"],
				"category_total": awl_coverage["category_total"],
				"category_hits": awl_coverage["category_hits"]
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
		f.close()
		return { "total": num_words, "hits": list(hits)}


	def get_awl_coverage(self, filename):
		words = {}
		f = open(filename)

		category = ""
		for word in f.readlines():
			if not word.startswith('\t'):
				category = word.strip()
			words[word.strip()] = category

		category_hits = set()
		hits = set(words.keys()).intersection(set(self.words.keys()))
		for hit in hits:
			category_hits.add(words[hit])

		return { 
			"words_total": len(words), 
			"words_hits": len(list(hits)), 
			"category_total": len(list(set(words.values()))), 
			"category_hits": len(category_hits)
		}



	def publish(self):
		pass
		# payload = {"stats" : json.dumps(self.stats)}
		# r = requests.put(self.publish_url + "/papers/" + self.paper_id + ".json", params=payload)


def set_paper_alive(publish_url, paper_id, alive):
	pass
	# payload = {"alive" : str(alive).lower()}
	# r = requests.put(publish_url + "/papers/" + paper_id + ".json", params=payload)


if __name__ == "__main__":
	logging.basicConfig(level=logging.INFO,
						format='%(asctime)s - %(message)s',
						datefmt='%Y-%m-%d %H:%M:%S')
	if len(sys.argv) != 4:
		print "Usage: python tracker.py <paper-file> <publish-host> <paper-id>"
		sys.exit()

	# Parse command line params
	filename = sys.argv[1]
	publish_url = sys.argv[2]
	paper_id = sys.argv[3]

	path = os.path.dirname(os.path.abspath(filename))

	# Observer setup + start
	event_handler = GamificationHandler(filename, publish_url, paper_id)
	observer = Observer()
	observer.schedule(event_handler, path=path, recursive=True)
	set_paper_alive(publish_url, paper_id, True);
	observer.start()
	try:
		while True:
			time.sleep(1)
	except KeyboardInterrupt:
		set_paper_alive(publish_url, paper_id, False);
		observer.stop()
	observer.join()