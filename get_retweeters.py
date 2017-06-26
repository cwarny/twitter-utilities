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
			with open('%s/%s_retweeters.json' % (dirname, tweet_id), 'w', newline='') as outfile:
				user_ids = t.get_retweeters(tweet_id)
				users = t.lookup_users(user_ids)
				for user in users:
					outfile.write(json.dumps(user) + '\n')