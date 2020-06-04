#!/usr/bin/env python3
# Copyright (c) 2018, Palo Alto Networks
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

# Authors: Scott Shoaf

import json
import sys
from datetime import datetime, timedelta

import click
import requests

import conf


def elk_index(elk_index_name):
    '''
    set up elasticsearch bulk load index
    :param elk_index_name: name of data index in elasticsearch
    :return: index tag to write as line in the output json file
    '''

    index_tag_full = {}
    index_tag_inner = {}
    index_tag_inner['_index'] = f'github-{elk_index_name}'
    index_tag_inner['_type'] = '_doc'
    index_tag_full['index'] = index_tag_inner

    return index_tag_full


def append_to_file(filename, data_dict, type):
    '''
    write to json file formatted for bulk elasticsearch input
    :param filename: name of the output file and data traffic type
    :param data_dict: dict contained one json entry
    :param action: 'a' append or 'w' write
    :return: index tag to write as line in the output json file
    '''

    index_tag_full = elk_index(type)

    with open(f'{filename}', 'a') as f:
        f.write(json.dumps(index_tag_full, indent=None, sort_keys=False) + "\n")
        f.write(json.dumps(data_dict, indent=None, sort_keys=False) + "\n")


def git_api_query_traffic(git_auth_token, org, repo, type):
    """
    grab github traffic stats and generate csv output
    curl -i -H "Authorization: token {git_token}" https://api.github.com/repos/{org}/{repo}/traffic/{type}
    :param git_token: personal auth token used for API access
    :param org: github org name used in API request
    :param repo: github repo name used in API request
    :param type: type of traffic including views, clones, referrers
    :return: query_reponse_dict
    """

    headers = {"Authorization": f"token {git_auth_token}"}
    git_api_url = f'https://api.github.com/repos/{org}/{repo}/traffic/{type}'

    try:
        git_traffic = requests.get(git_api_url, headers=headers)
        # print('View stats request posted to github')
        git_traffic.raise_for_status()
    except requests.exceptions.HTTPError:
        print(git_traffic)
        print(git_traffic.text)
        print('\nCorrect errors and rerun the application\n')
        sys.exit()

    query_response_dict = json.loads(git_traffic.text)

    return query_response_dict


@click.command()
@click.option("-a", "--git_auth_token", help="git auth token", type=str, default='')
@click.option("-f", "--filename", help="github traffic type", type=str, default='')
@click.option("-d", "--days_ago", help="look back num days ago (max 14)", type=int, default='')
def cli(git_auth_token, filename, days_ago):
    """
    grab github traffic stats and generate csv output
    :param git_token: personal auth token used for API access
    :param filenamme: csv list of orgs and repos
    :return: None
    """

    # timestamp to be added to the file name
    filedate = datetime.now().strftime('%Y-%m-%dT%H-%M-%SZ')

    # create empty json output files
    for type in ['daily', 'referrer']:
        with open(f'{type}_output/{type}-{filedate}.json', 'w') as f:
            continue

    # input list of orgs and repos
    with open(filename) as f:
        print('\nreading org and repo list from file\n')

        for org_repo in f:
            org_repo_list = org_repo.rstrip().split(',')
            org = org_repo_list[0]
            repo = org_repo_list[1]
            # type = org_repo_list[2]  --> option to add to the list

            print(f'getting stats for {org}/{repo}')

            stats_dict = {}
            stats_dict['metrics.github.org'] = org
            stats_dict['metrics.github.repo'] = repo
            # stats_dict['metric.github.repo.type'] = type
            # stats_dict['metric.github.repo.url'] = f'https://github.com/{org}/{repo}'

            # get views and clones traffic stats
            repo_traffic_views = git_api_query_traffic(git_auth_token, org, repo, 'views')
            repo_traffic_clones = git_api_query_traffic(git_auth_token, org, repo, 'clones')

            # set start date for extraction of github query values
            start_date = datetime.now() - timedelta(days=days_ago)
            stop_date = datetime.now() - timedelta(minutes=1)
            item_date = start_date

            # generate daily stats and write to dict for csv output
            while item_date < stop_date:
                stats_dict['date'] = item_date.strftime('%Y-%m-%dT00:00:00Z')

                # grab views metrics based on current date interval or set to zero if no entry
                date_pos = next((index for (index, d) in enumerate(repo_traffic_views['views']) if
                                 d["timestamp"] == stats_dict['date']), None)

                if date_pos is not None:
                    stats_dict[f'metrics.github.views.daily.count'] = repo_traffic_views['views'][date_pos]['count']
                    stats_dict[f'metrics.github.views.daily.uniques'] = repo_traffic_views['views'][date_pos]['uniques']
                else:
                    stats_dict[f'metrics.github.views.daily.count'] = 0
                    stats_dict[f'metrics.github.views.daily.uniques'] = 0

                # grab clones metrics based on current date interval or set to zero if no entry
                date_pos = next((index for (index, d) in enumerate(repo_traffic_clones['clones']) if
                                 d["timestamp"] == stats_dict['date']), None)
                if date_pos is not None:
                    stats_dict[f'metrics.github.clones.daily.count'] = repo_traffic_clones['clones'][date_pos]['count']
                    stats_dict[f'metrics.github.clones.daily.uniques'] = repo_traffic_clones['clones'][date_pos][
                        'uniques']
                else:
                    stats_dict[f'metrics.github.clones.daily.count'] = 0
                    stats_dict[f'metrics.github.clones.daily.uniques'] = 0

                if item_date + timedelta(days=1) > stop_date:
                    # 14day summary stats added to the prior day stats
                    stats_dict[f'metrics.github.views.summary.count'] = repo_traffic_views['count']
                    stats_dict[f'metrics.github.views.summary.uniques'] = repo_traffic_views['uniques']
                    stats_dict[f'metrics.github.clones.summary.count'] = repo_traffic_clones['count']
                    stats_dict[f'metrics.github.clones.summary.uniques'] = repo_traffic_clones['uniques']

                append_to_file(f'daily_output/daily-{filedate}.json', stats_dict, 'daily')
                item_date = item_date + timedelta(days=1)

            # get referrers traffic stats
            repo_traffic = git_api_query_traffic(git_auth_token, org, repo, 'popular/referrers')

            for item in repo_traffic:
                # generates a unique entry for each date-repo-referrer
                stats_dict = {}
                stats_dict['date'] = item_date.strftime('%Y-%m-%dT00:00:00Z')
                stats_dict['metrics.github.org'] = org
                stats_dict['metrics.github.repo'] = repo
                stats_dict['metrics.github.referrer.referrer'] = item['referrer']
                stats_dict['metrics.github.referrer.count'] = item['count']
                stats_dict['metrics.github.referrer.uniques'] = item['uniques']

                append_to_file(f'referrer_output/referrer-{filedate}.json', stats_dict, 'referrer')

    # print out the elasticSearch bulk load curl commands
    print('\nUse curl -XDELETE [url]:[port]/index to delete data from the index')
    print('use the XPOST curl command to load json data to elasticSearch')
    print('add -u with username:password if security features enabled\n')

    for type in ['daily', 'referrer']:
        print(
            f'curl -s -XPOST \'http://{conf.elastic_url_port}/_bulk\' --data-binary @{type}_output/{type}-{filedate}.json -H \"Content-Type: application/x-ndjson\" \n')


if __name__ == '__main__':
    cli()
