from twitter import Twitter
import json
import csv

with open('credentials.csv') as infile:
	reader = csv.reader(infile)
	t = Twitter(list(reader)[1:])

with open('data/user_ids.txt') as infile:
	retweeters = set([line.strip() for line in infile])

seen = set([])

def recursive_get_followers(user_ids, tree, n=0):
	for user_id in user_ids:
		tree[user_id] = {}
		if user_id not in seen:
			seen.add(user_id)
			if len(seen) >= len(retweeters):
				return
			followers = [fid for fid in t.get_followers(user_id, stringify_ids=True) if fid in retweeters]
			if n <= 5:
				recursive_get_followers(followers, tree[user_id], n+1)

with open('data/tree.json', 'w') as outfile:
	tree = {}
	recursive_get_followers(['1339835893'], tree)
	json.dump(tree, outfile)