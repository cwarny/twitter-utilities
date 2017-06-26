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
			tweet_id = line.strip()
			with open('%s/%s_retweets.json' % (dirname, tweet_id), 'w', newline='') as outfile:
				tweets = t.get_retweets(tweet_id)
				for tweet in tweets:
					outfile.write(json.dumps(tweet) + '\n')