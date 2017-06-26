import json
import csv
from twitter_normalize_utils import process_tweets
import sys
import os

fieldnames = {
	'users': ['contributors_enabled','created_at','default_profile','default_profile_image','description','favourites_count','follow_request_sent','following','followers_count','friends_count','geo_enabled','id','id_str','is_translator','lang','listed_count','location','name','notifications','profile_background_color','profile_background_image_url','profile_background_image_url_https','profile_background_tile','profile_banner_url','profile_image_url','profile_image_url_https','profile_link_color','profile_sidebar_border_color','profile_sidebar_fill_color','profile_text_color','profile_use_background_image','protected','screen_name','show_all_inline_media','statuses_count','time_zone','url','utc_offset','verified','withheld_scope','status_id'],
	'tweets': ['coordinates.lat','coordinates.lon','coordinates.type','created_at','favorite_count','favorited','filter_level','id','id_str','in_reply_to_screen_name','in_reply_to_status_id','in_reply_to_status_id_str','in_reply_to_user_id','in_reply_to_user_id_str','lang','place','possibly_sensitive','quoted_status_id','quoted_status_id_str','retweet_count','retweeted','retweeted_status_id','source','text','truncated','user_id','withheld_copyright','withheld_scope','place_id'],
	'countries': ['tweet_id','user_id','country_code'],
	'contributors': ['tweet_id','id','id_str','screen_name'],
	'hashtags': ['tweet_id','user_id','start','stop','text','level'],
	'urls': ['tweet_id','user_id','start','stop','display_url','expanded_url','url','level'],
	'media': ['tweet_id','user_id','start','stop','display_url','expanded_url','id','id_str','media_url','media_url_https','source_status_id','source_status_id_str','type','url','level'],
	'user_mentions': ['tweet_id','user_id','start','stop','id','id_str','name','screen_name','level'],
	'symbols': ['tweet_id','user_id','start','stop','text','level'],
	'places': ['attributes.street_address','attributes.locality', 'attributes.region','attributes.iso3','attributes.postal_code','attributes.phone','attributes.twitter','attributes.url','bounding_box','country','country_code','full_name','id','name','place_type','url']
}

if __name__ == '__main__':
	files = []
	writers = {}

	ifn = sys.argv[1]

	filepath = os.path.normpath(ifn)
	ifbasename = os.path.basename(filepath)
	dirname = os.path.dirname(filepath) or '.'

	outdir = dirname + '/' + ifbasename.split('.')[0]

	os.mkdir(outdir)

	for fn, fields in fieldnames.items():
		f = open('%s/%s.csv' % (outdir, fn), 'w', newline='', encoding='utf-8')
		files.append(f)
		w = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
		writers[fn] = w
		w.writeheader()

	with open(ifn) as infile:
		tweets = (json.loads(line) for line in infile)
		documents = process_tweets(tweets)
		for doc in documents:
			writers[doc['type']].writerow(doc['document'])

	for f in files:
		f.close()