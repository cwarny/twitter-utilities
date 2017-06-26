from twitter import Twitter
import time
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
		reader = csv.DictReader(infile)
		for row in reader:
			with open('%s/%s.json' % (dirname, row['query_id']), 'w', newline='') as outfile:
				tweets = t.search(row['query'], row['start_date'], row['end_date'])
				for tweet in tweets:
					outfile.write(json.dumps(tweet) + '\n')
			