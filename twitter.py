import twython
from twython import Twython
import time
from datetime import datetime as dt
from datetime import timedelta as td
import sys
from itertools import zip_longest
from random import randint

def grouper(iterable, n, fillvalue=None):
	"Collect data into fixed-length chunks or blocks"
	# grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
	args = [iter(iterable)] * n
	return zip_longest(*args, fillvalue=fillvalue)

class Twitter:
	def __init__(self, credentials):
		self.credentials = [
			{
				'params': c,
				'last_rate_limit_hit': dt(1970,1,1)
			}
			for c in credentials
		]
		self.t = Twython(*self.credentials[0]['params'])

	def robust_request(self, func_name, n=1, **kwargs):
		try:
			resp = getattr(self.t, func_name)(**kwargs)
		except twython.exceptions.TwythonRateLimitError as e:
			self.credentials[0]['last_rate_limit_hit'] = dt.now()
			self.credentials = sorted(self.credentials, key=lambda e: e['last_rate_limit_hit'])
			if (dt.now() - self.credentials[0]['last_rate_limit_hit']).seconds/60 < 15:
				print(e, e.msg, e.error_code, file=sys.stderr)
				print('All credentials used up. Sleeping for 15 mins.', file=sys.stdout)
				time.sleep(15*60)
				return self.robust_request(func_name, **kwargs)
			else:
				print('Swapping credentials.', file=sys.stdout)
				self.t = Twython(*self.credentials[0]['params'])
				return self.robust_request(func_name, **kwargs)
		except twython.exceptions.TwythonError as e:
			print(e, file=sys.stdout)
			time.sleep((2 ** n) + (randint(0, 1000) / 1000))
			if n > 5:
				print('Skipping this request.', file=sys.stdout)
				return None
			else:
				return self.robust_request(func_name, n+1,**kwargs)
		return resp

	def search(self, q, start_date=None, end_date=None):
		kwargs = { 'q': q, 'count': 100 }
		if end_date:
			kwargs['until'] = (dt.strptime(end_date, '%Y-%m-%d') + td(1)).strftime('%Y-%m-%d')
		if start_date:
			start_date = dt.strptime(start_date, '%Y-%m-%d')
		while True:
			tweets = self.robust_request('search', **kwargs)['statuses']
			if not tweets:
				break
			max_id = min([tweet['id'] for tweet in tweets])
			if 'max_id' in kwargs and max_id == kwargs['max_id']:
				break
			if start_date:
				tweets = [t for t in tweets if dt.strptime(t['created_at'], '%a %b %d %H:%M:%S +0000 %Y') >= start_date]
			if not tweets:
				break
			kwargs['max_id'] = max_id
			for t in tweets:
				yield t

	def get_user_timeline(self, **kwargs):
		kwargs.update({ 'count': 200 })
		while True:
			tweets = self.robust_request('get_user_timeline', **kwargs)
			if not tweets:
				break
			max_id = min([tweet['id'] for tweet in tweets])
			if 'max_id' in kwargs and max_id == kwargs['max_id']:
				break
			kwargs['max_id'] = max_id
			for t in tweets:
				yield t

	def get_friends(self, user_id):
		M = 75000
		m = 0
		kwargs = { 'user_id': user_id, 'count': 5000, 'cursor': -1 }
		while kwargs['cursor'] != 0 and m < M:
			resp = self.robust_request('get_friends_ids', **kwargs)
			if not resp:
				break
			kwargs['cursor'] = resp['next_cursor']
			m += len(resp['ids'])
			for _id in resp['ids']:
				yield _id

	def get_followers(self, **kwargs):
		M = 75000
		m = 0
		kwargs.update({ 'count': 5000, 'cursor': -1 })
		while kwargs['cursor'] != 0:
			resp = self.robust_request('get_followers_ids', **kwargs)
			if not resp:
				break
			kwargs['cursor'] = resp['next_cursor']
			m += len(resp['ids'])
			for _id in resp['ids']:
				yield _id

	def lookup_users(self, ids):
		for ids_chunk in grouper(ids, 100):
			ids_chunk = [str(_id) for _id in ids_chunk if _id]
			user_ids = ','.join(ids_chunk)
			if user_ids:
				kwargs = { 'user_id': user_ids }
				users = self.robust_request('lookup_user', **kwargs)
				if not users:
					break
				if users:
					for user in users:
						yield user

	def get_retweets(self, _id):
		kwargs = { 'id': _id, 'count': 100 }
		tweets = self.robust_request('get_retweets', **kwargs)
		if tweets:
			for t in tweets:
				yield t

	def get_retweeters(self, _id):
		M = 1500
		m = 0
		kwargs = { 'id': _id, 'count': 100, 'cursor': -1 }
		while kwargs['cursor'] != 0 and m < M:
			resp = self.robust_request('get_retweeters_ids', **kwargs)
			if not resp:
				break
			kwargs['cursor'] = resp['next_cursor']
			m += len(resp['ids'])
			for _id in resp['ids']:
				yield _id