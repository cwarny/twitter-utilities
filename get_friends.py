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
			user_id = line.strip()
			with open('%s/%s_friends.json' % (dirname, user_id), 'w', newline='') as outfile:
				friends_ids = t.get_friends(user_id)
				friends = t.lookup_users(friends_ids)
				for friend in friends:
					outfile.write(json.dumps(friend) + '\n')