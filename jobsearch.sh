python get_followers.py data/user_ids.txt
python findcompanies.py
tail -n+2 data/mentions.csv | awk -F, '{print tolower($1)}' | sort | uniq -c | sort -k1,1rn | awk '{print $2}' | head -n100 > data/topcompanies.txt
python get_timelines.py data/topcompanies.txt
python findpostings.py
python jobkeywords.py