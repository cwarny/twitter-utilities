import json

def process_tweets(tweets):
	for tweet in tweets:
		yield from process_tweet(tweet)

def process_tweet(tweet):
	tweet['user_id'] = tweet['user']['id']
	yield from process_user(tweet.pop('user'))

	if 'coordinates' in tweet and tweet['coordinates']:
		tweet['coordinates.lon'], tweet['coordinates.lat'] = tweet['coordinates']['coordinates']
		tweet['coordinates.type'] = tweet['coordinates']['type']

	if 'place' in tweet and tweet['place']: 
		tweet['place_id'] = tweet['place']['id']
		yield from process_place(tweet.pop('place'))
	if 'quoted_status' in tweet and tweet['quoted_status']: 
		yield from process_tweet(tweet.pop('quoted_status'))
	if 'retweeted_status' in tweet and tweet['retweeted_status']: 
		tweet['retweeted_status_id'] = tweet['retweeted_status']['id']
		yield from process_tweet(tweet.pop('retweeted_status'))

	if 'withheld_in_countries' in tweet and tweet['withheld_in_countries']: 
		yield from process_withheld_in_countries(tweet.pop('withheld_in_countries'), tweet_id=tweet['id'])
	if 'contributors' in tweet and tweet['contributors']: 
		yield from process_contributors(tweet.pop('contributors'), tweet['id'])
	if 'entities' in tweet and tweet['entities']: 
		yield from process_entities(tweet.pop('entities'), tweet_id=tweet['id'])

	yield {
		'type': 'tweets',
		'document': tweet
	}

def process_entities(entities, tweet_id=None, user_id=None):
	if tweet_id:
		for k,v in entities.items():
			for item in v:
				item['start'], item['stop'] = item['indices']
				item['tweet_id'] = tweet_id
				
				yield {
					'type': k,
					'document': item
				}

	elif user_id:
		for k1,v1 in entities.items():
			for k2,v2 in v1.items():
				for item in v2:
					item['start'], item['stop'] = item['indices']
					item['user_id'] = user_id
					item['level'] = k1
					
					yield {
						'type': k2,
						'document': item
					}

def process_place(place):
	place.update({ 'attributes.%s' % k: v for k,v in place['attributes'].items() })
	place['bounding_box'] = json.dumps(place['bounding_box'])
	
	yield {
		'type': 'places',
		'document': place
	}

def process_user(user):
	if 'withheld_in_countries' in user and user['withheld_in_countries']:
		yield from process_withheld_in_countries(user.pop('withheld_in_countries'), user_id=user['id'])
	if 'entities' in user and user['entities']: 
		yield from process_entities(user.pop('entities'), user_id=user['id'])
	if 'status' in user and user['status']:
		user['status_id'] = user['status']['id']

	yield {
		'type': 'users',
		'document': user
	}

def process_users(users):
	for user in users:
		yield from process_user(user)

def process_withheld_in_countries(withheld_in_countries, tweet_id=None, user_id=None):
	for c in withheld_in_countries:
		document = {}
		if tweet_id:
			document['tweet_id'] = tweet_id
		elif user_id:
			document['user_id'] = user_id
		document.update({'country_code':c})
		
		yield {
			'type': 'countries',
			'document': document
		}

def process_contributors(contributors, tweet_id=None):
	for contributor in contributors:
		contributor.update({'tweet_id':tweet_id})
		
		yield {
			'type': 'contributors',
			'document': contributor
		}