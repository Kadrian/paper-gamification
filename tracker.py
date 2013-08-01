import os
import sys
import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from watchdog.events import FileModifiedEvent

class GamificationHandler(FileSystemEventHandler):
	
	def __init__(self, filename):
		FileSystemEventHandler.__init__(self)

		self.filename = filename


	def on_modified(self, event):
		if type(event) == FileModifiedEvent:
			if os.path.abspath(self.filename) == event.src_path:
				self.do_gamification()

	def do_gamification(self):
		f = open(self.filename)
		
		# Count words
		num_words = 0
		for line in f.readlines():
			words = line.split(" ")
			for w in words:
				if w.strip() != "" and w.isalnum():
					num_words += 1

		logging.info("Total num of words: " + str(num_words))


if __name__ == "__main__":

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