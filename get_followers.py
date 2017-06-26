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
			with open('%s/%s_followers.json' % (dirname, screen_name), 'w', newline='') as outfile:
				followers_ids = t.get_followers(screen_name=screen_name)
				followers = t.lookup_users(followers_ids)
				for follower in followers:
					outfile.write(json.dumps(follower) + '\n')