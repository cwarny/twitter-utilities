import json
import networkx as nx
from networkx.readwrite import json_graph
from itertools import filterfalse
from datetime import datetime as dt
import sys

def unique_everseen(iterable, key=None):
	"List unique elements, preserving order. Remember all elements ever seen."
	# unique_everseen('AAAABBBCCDAABBB') --> A B C D
	# unique_everseen('ABBCcAD', str.lower) --> A B C D
	seen = set()
	seen_add = seen.add
	if key is None:
		for element in filterfalse(seen.__contains__, iterable):
			seen_add(element)
			yield element
	else:
		for element in iterable:
			k = key(element)
			if k not in seen:
				seen_add(k)
				yield element

with open('data/tree.json') as infile:
	jsn = json.load(infile)

DG = nx.DiGraph()

def traverse(tree):
	for parent,children in tree.items():
		for child in children.keys():
			DG.add_edge(parent,child)
		traverse(children)

traverse(jsn)

all_nodes = DG.nodes()

with open('data/1.json') as infile:
	tweets = (json.loads(line) for line in infile)
	retweets = (t for t in tweets if 'retweeted_status' in t and t['retweeted_status']['user']['id_str'] == '1339835893' and t['user']['id_str'] in all_nodes)
	for tweet in unique_everseen(retweets, lambda t:t['user']['id_str']):
		DG.node[tweet['user']['id_str']]['timestamp'] = dt.strptime(tweet['created_at'],'%a %b %d %H:%M:%S +0000 %Y')
		DG.node[tweet['user']['id_str']].update(tweet)

root_user_id = tweet['retweeted_status']['user']['id_str']
root_tweet = tweet['retweeted_status']
DG.node[root_user_id]['timestamp'] = dt.strptime(root_tweet['created_at'],'%a %b %d %H:%M:%S +0000 %Y')
DG.node[root_user_id].update(root_tweet)

ebunch = []
for n0,n1 in DG.edges_iter():
	if DG.node[n1]['timestamp'] <= DG.node[n0]['timestamp']:
		ebunch.append((n0,n1))
	else:
		DG[n0][n1]['timedelta'] = (DG.node[n1]['timestamp']-DG.node[n0]['timestamp']).seconds

if ebunch:
	DG.remove_edges_from(ebunch)

for node,data in DG.nodes_iter(data=True):
	del data['timestamp']

DG1 = nx.DiGraph()
DG2 = nx.DiGraph()

for node,data in DG.nodes_iter(data=True):
	predecessors = DG.predecessors(node)
	in_edges = DG.in_edges(node, data=True)
	
	if not predecessors:
		continue
	elif len(predecessors) == 1:
		DG1.add_edge(predecessors[0],node)
		DG2.add_edge(predecessors[0],node)
	else:	
		DG1.add_edge(max(predecessors, key=lambda p: DG.node[p]['user']['followers_count']), node)
		DG2.add_edge(*min(in_edges, key=lambda e: e[2]['timedelta'])[:-1])

	DG1.node[node].update(data)
	DG2.node[node].update(data)

DG1.node[root_user_id].update(root_tweet)
DG2.node[root_user_id].update(root_tweet)

nbunch = []
for node,data in DG1.nodes_iter(data=True):
	try:
		data['level'] = len(nx.shortest_path(DG1, root_user_id, node))
	except nx.exception.NetworkXNoPath as e:
		print(e, file=sys.stdout)
		nbunch.append(node)

if nbunch:
	DG1.remove_nodes_from(nbunch)

nbunch = []
for node,data in DG2.nodes_iter(data=True):
	try:
		data['level'] = len(nx.shortest_path(DG2, root_user_id, node))
	except nx.exception.NetworkXNoPath as e:
		print(e, file=sys.stdout)
		nbunch.append(node)

if nbunch:
	DG2.remove_nodes_from(nbunch)

with open('data/g1.json', 'w') as outfile1, open('data/g2.json', 'w') as outfile2:
	json.dump(json_graph.node_link_data(DG1), outfile1, indent=4)
	json.dump(json_graph.node_link_data(DG2), outfile2, indent=4)

def get_children(g,node):
	children = []
	for s in g.successors(node):
		data = g.node[s]
		children.append({**data,**{'name':s, 'children': get_children(g,s)}})
	return children

with open('data/h1.json','w') as outfile1, open('data/h2.json','w') as outfile2:
	json.dump({**root_tweet, **{
		'name': root_user_id,
		'children': get_children(DG1,root_user_id)
	}}, outfile1, indent=4)
	json.dump({**root_tweet, **{
		'name': root_user_id,
		'children': get_children(DG2,root_user_id)
	}}, outfile2, indent=4)