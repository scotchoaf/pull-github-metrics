# Git Metrics

read a csv file with a list of github orgs and repos
output is repo traffic stats for views, clones, and top referrers

Uses a github personal auth token for authentication

    python git_metrics_json_out.py -a {auth token} -f {repo list} -d {number of days to look back}
 
output of `git_metrics_json_out.py` is formatted for bulk loading to elasticsearch using the commands:

```angular2
curl -XDELETE http://localhost:9200/daily
curl -s -XPOST 'http://localhost:9200/_bulk' --data-binary @daily.json -H "Content-Type: application/x-ndjson" 

curl -XDELETE http://localhost:9200/referrer
curl -s -XPOST 'http://localhost:9200/_bulk' --data-binary @referrer.json -H "Content-Type: application/x-ndjson" 

```

Only use delete for testing and you wish to delete the existing index and data.
