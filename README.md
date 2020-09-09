# Git Metrics

Two modes:

    * JSON output for bulk loading into Elasticsearch
    * quick output to screen for single org/repo
    
### JSON output mode

read a csv file with a list of github orgs and repos
output is repo traffic stats for views, clones, and top referrers

Uses a github personal auth token for authentication

    python git_metrics_json_out.py -a {auth token} -f {repo list} -d {number of days to look back}
 
output of `daily-{run date}` and `referrer-{run date}` are formatted for bulk loading to elasticsearch using the commands:

```bash

curl -s -XPOST 'http://localhost:9200/_bulk' --data-binary @daily.json -H "Content-Type: application/x-ndjson" 
curl -s -XPOST 'http://localhost:9200/_bulk' --data-binary @referrer.json -H "Content-Type: application/x-ndjson" 

```

Use XDELETE in the event you need to delete a specific index in Elasticsearch

```bash
curl -XDELETE http://localhost:9200/daily
curl -XDELETE http://localhost:9200/referrer
```

### Quick output mode

use input values for a quick view and to test access to a org and repo.

    python git_metrics_quick.py -a {auth token} -o {org name} -r {repo name}
    
> default org is PaloAltoNetworks

Output display will show view, clone, and referrer data

## Git metrics raw CURL commands

```bash
curl -i -H "Authorization: token {auth token}" https://api.github.com/repos/{org name}/{repo name}/traffic/views
curl -i -H "Authorization: token {auth token}" https://api.github.com/repos/{org name}/{repo name}/traffic/clones
curl -i -H "Authorization: token {auth token}" https://api.github.com/repos/{org name}/{repo name}/traffic/popular/referrers
```
