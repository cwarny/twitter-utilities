# Twitter Factory

Twitter Factory is a set of Python scripts outlining different process flows to get different types of data from the Twitter API and formatting them for subsequent analytical processes. These scripts will seamlessly handle Twitter API rate limits and swapping through different Twitter API credentials.

## Prerequisites

You will need to following things properly installed on your computer:

* [Git](http://git-scm.com/)
* [Python 3](http://python.org)

## Installation

* `git clone <repository-url>` this repository
* change into the new directory
* `pip install -r requirements.txt`
* Add a CSV file named `credentials.csv` at the root of this directory containing one or more Twitter API credentials (go to https://apps.twitter.com/ to create them) with the four following columns:
	* APP_KEY
	* APP_SECRET
	* OAUTH_TOKEN
	* OAUTH_TOKEN_SECRET

The more different credentials you add to the credentials file, the more data you will be able to get faster. The [Twitter API rate limits](https://dev.twitter.com/rest/public/rate-limits) can be quite strict.

## Process flows

Here is a table summarizing the different possible process flows:

| Input     | Process name   | Output | Output format              | Comment                                                                                             |
|-----------|----------------|--------|----------------------------|-----------------------------------------------------------------------------------------------------|
| user ids  | get_timelines  | tweets | *user_id*_timeline.json    | Twitter only allows to retrieve up to 3,200 tweets in the past, starting from the last tweet        |
| user ids  | get_followers  | users  | *user_id*_followers.json   | Script arbitrarily caps the number of followers returned to 75,000. Contact developer for more info |
| user ids  | get_friends    | users  | *user_id*_friends.json     | Script arbitrarily caps the number of friends returned to 75,000. Contact developer for more info   |
| tweet ids | get_retweeters | users  | *tweet_id*_retweeters.json | Script arbitrarily caps the number of retweeters returned to 1,500. Contact developer for more info |
| tweet ids | get_retweets   | tweets | *tweet_id*_retweets.json   |                                                                                                     |
| queries   | search_tweets  | tweets | *query_id*.json            |                                                                                                     |

Formats are as follows:

* Inputs
	* User ids: text file with each user id on a separate line
	* Tweet ids: text file with each tweet id on a separate line
	* Queries: CSV file with four columns:
		* query_id
		* [query](https://dev.twitter.com/rest/public/search)
		* start_date (formatted `YYYY-mm-dd`)
		* end_date (formatted `YYYY-mm-dd`)
* Outputs
	* Users: JSON file with each JSON-formatted user object on a separate line
	* Tweets: JSON file with each JSON-formatted tweet object on a separate line

For each line of input, an output file will be created. So if the user ids file has two user ids (on two separate lines), there will be two output files. To run the processes: `python <process name>.py <input file>`. Outputs will be in same folder as inputs.

## Output normalization

Many analytical processes require data to be in tabular format. For that end, we created two scripts that output the following tables in a new folder at the same location as the input file. Output folder will have the same name as the input file.

| table         | normalize_tweets.py | normalize_users.py |
|---------------|:-------------------:|:------------------:|
| tweets        |          x          |                    |
| users         |          x          |          x         |
| places        |          x          |                    |
| urls          |          x          |          x         |
| hashtags      |          x          |          x         |
| media         |          x          |          x         |
| user_mentions |          x          |          x         |
| symbols       |          x          |          x         |
| countries     |          x          |          x         |
| contributors  |          x          |                    |

For more information on the tables and their fields, check out the [Twitter API overview](https://dev.twitter.com/overview/api) describing the different objects it returns.

To run the scripts: 

* `python normalize_tweets.py <input file with JSON-formatted tweet object on each line>`
* `python normalize_users.py <input file with JSON-formatted user object on each line>`

Tip: if you have multiple files to normalize, use a **for** loop on the command line to make this process more efficient, rather than having to manually run the script for each file.

The relationships between the different tables are as follows. Format is 

*table_name* *source_cardinality*--*primary_key*-->*destination_cardinality* *table_name*

* tweets 1--user_id-->1 users
* tweets 1--place_id-->1 places
* urls n--tweet_id-->1 tweets
* hashtags n--tweet_id-->1 tweets
* media n--tweet_id-->1 tweets
* user_mentions n--tweet_id-->1 tweets
* symbols n--tweet_id-->1 tweets
* urls n--user_id-->1 users
* hashtags n--user_id-->1 users
* media n--user_id-->1 users
* user_mentions n--user_id-->1 users
* symbols n--user_id-->1 users
* countries n--tweet_id-->1 tweets
* countries n--user_id-->1 users
* contributors n--tweet_id-->1 tweets
* tweets 1--quoted_status_id-->1 tweets
* tweets 1--retweeted_status_id-->1 tweets

The `hashtags`, `media`, `urls`, `user_mentions`, and `symbols` tables (the five different types of twitter 'entities') contain the columns `tweet_id` and `user_id`. These two columns are mutually exclusive: if one's populated, the other one is not. Twitter entities can be found in either a user profile or a tweet. If `tweet_id` is populated, that is the id of the tweet this entity was found in. If `user_id` is populated, that is the id of the user whose profile that entity was found on.

When the columns `retweeted_status_id` or `quoted_status_id` are populated for a tweet, you should be able to find those tweets referred to in the same table.

Finally, it is possible some tweets or users will be duplicated in these tables.