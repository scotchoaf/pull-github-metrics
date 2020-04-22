# Git Metrics

read a file with a list of github orgs and repos
output is repo traffic stats for views, clones, and top referrers

Uses github personal auth token


quick load to elasticsearch when using the json option.
includes index values delete and then post of updated values



```angular2
curl -XDELETE http://localhost:9200/daily
curl -s -XPOST 'http://localhost:9200/_bulk' --data-binary @daily.json -H "Content-Type: application/x-ndjson" 

curl -XDELETE http://localhost:9200/summary
curl -s -XPOST 'http://localhost:9200/_bulk' --data-binary @summary.json -H "Content-Type: application/x-ndjson" 

curl -XDELETE http://localhost:9200/referrer
curl -s -XPOST 'http://localhost:9200/_bulk' --data-binary @referrer.json -H "Content-Type: application/x-ndjson" 

```