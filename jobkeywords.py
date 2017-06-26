import re
import pandas as pd
from datetime import timedelta as td
from datetime import datetime as dt
from collections import defaultdict
from stop_words import get_stop_words

stopwords = get_stop_words('en') + ['http','https','t','co']

TOKENS = re.compile('\w+') # Poor man's tokenizer

df = pd.read_csv('data/jobpostings.csv', parse_dates=['created_at'], date_parser=lambda x: pd.datetime.strptime(x, '%a %b %d %H:%M:%S +0000 %Y'))
# then = dt.now() - td(60)
# df_filtered = df[df.created_at > then]

tokens = defaultdict(list)
for _,row in df.iterrows():
	words = TOKENS.findall(row['text'])
	idx = row['key_token_idx']
	for word in [w for w in words[idx+1:] if w not in stopwords][:4]: # only looking at non-stopwords words right after a job keyword
		tokens['screen_name'].append(row['screen_name'])
		tokens['word'].append(word.lower())

tokens = pd.DataFrame(tokens)

agg = tokens.groupby(['screen_name','word']).agg('size')
agg = agg[agg > 1]
g = agg.groupby(level=0,group_keys=False)

g.nlargest(100).reset_index().to_csv('data/keywords.csv',index=False)