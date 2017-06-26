from twitter import Twitter
import sys
import json
import csv
import os

if __name__ == '__main__':
	ifn = sys.argv[1]

	filepath = os.path.normpath(ifn)
	ifbasename = os.path.basename(filepath)
	dirname = os.path.dirname(filepath) or '.'

	with open('credentials.csv') as infile:
		reader = csv.reader(infile)
		t = Twitter(list(reader)[1:])

	with open(ifn) as infile:
		for line in infile:
			screen_name = line.strip()
			with open('%s/%s_timeline.json' % (dirname, screen_name), 'w', newline='') as outfile:
				for tweet in t.get_user_timeline(screen_name=screen_name):
					outfile.write(json.dumps(tweet) + '\n')