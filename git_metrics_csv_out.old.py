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

import csv
import json
import sys
from datetime import datetime

import click
import requests


def create_output_files():
    """
    generate emtpty output files with a header row
    """

    # create output summary stats file with header row
    with open('14day_summary_stats.csv', 'w') as f:
        writer = csv.DictWriter(
            f, fieldnames=['metrics.github.summary.date',
                           'metrics.github.summary.type',
                           'metrics.github.summary.org',
                           'metrics.github.summary.repo',
                           'metrics.github.summary.count',
                           'metrics.github.summary.uniques']
        )
        writer.writeheader()

    # create output daily stats file with header row
    with open('daily_stats.csv', 'w') as f:
        writer = csv.DictWriter(
            f, fieldnames=['metrics.github.daily.date',
                           'metrics.github.daily.type',
                           'metrics.github.daily.org',
                           'metrics.github.daily.repo',
                           'metrics.github.daily.count',
                           'metrics.github.daily.uniques']
        )
        writer.writeheader()

    # create output referrer stats file with header row
    with open('referrer_stats.csv', 'w') as f:
        writer = csv.DictWriter(
            f, fieldnames=['metrics.github.referrer.date',
                           'metrics.github.referrer.type',
                           'metrics.github.referrer.org',
                           'metrics.github.referrer.repo',
                           'metrics.github.referrer.referrer',
                           'metrics.github.referrer.count',
                           'metrics.github.referrer.uniques']
        )
        writer.writeheader()


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
def cli(git_auth_token, filename):
    """
    grab github traffic stats and generate csv output
    :param git_token: personal auth token used for API access
    :param filenamme: csv list of orgs and repos
    :return: None
    """

    # generate output files with header rows
    create_output_files()

    # input list of orgs and repos
    with open(filename) as f:
        print('\nreading org and repo list from file\n')

        for org_repo in f:
            org_repo_list = org_repo.rstrip().split(',')
            org = org_repo_list[0]
            repo = org_repo_list[1]

            print(f'getting stats for {org}/{repo}')
            # get views and clones traffic stats
            for type in ['views', 'clones']:

                # get and output traffic data and write to dict for csv output
                repo_traffic = git_api_query_traffic(git_auth_token, org, repo, type)

                stats_dict = {}
                stats_dict['metrics.github.summary.date'] = datetime.now()
                stats_dict['metrics.github.summary.type'] = type
                stats_dict['metrics.github.summary.org'] = org
                stats_dict['metrics.github.summary.repo'] = repo
                stats_dict['metrics.github.summary.count'] = repo_traffic['count']
                stats_dict['metrics.github.summary.uniques'] = repo_traffic['uniques']

                # create output summary stats file
                with open('14day_summary_stats.csv', 'a') as f:
                    writer = csv.DictWriter(
                        f, fieldnames=['metrics.github.summary.date',
                                       'metrics.github.summary.type',
                                       'metrics.github.summary.org',
                                       'metrics.github.summary.repo',
                                       'metrics.github.summary.count',
                                       'metrics.github.summary.uniques']
                    )
                    writer.writerow(stats_dict)

                # generate daily stats and write to dict for csv output
                for item in repo_traffic[type]:
                    stats_dict = {}
                    stats_dict['metrics.github.daily.date'] = item['timestamp']
                    stats_dict['metrics.github.daily.type'] = type
                    stats_dict['metrics.github.daily.org'] = org
                    stats_dict['metrics.github.daily.repo'] = repo
                    stats_dict['metrics.github.daily.count'] = item['count']
                    stats_dict['metrics.github.daily.uniques'] = item['uniques']

                    # create output daily stats file
                    with open('daily_stats.csv', 'a') as f:
                        writer = csv.DictWriter(
                            f, fieldnames=['metrics.github.daily.date',
                                           'metrics.github.daily.type',
                                           'metrics.github.daily.org',
                                           'metrics.github.daily.repo',
                                           'metrics.github.daily.count',
                                           'metrics.github.daily.uniques']
                        )
                        writer.writerow(stats_dict)

            # get referrers traffic stats
            repo_traffic = git_api_query_traffic(git_auth_token, org, repo, 'popular/referrers')

            for item in repo_traffic:
                stats_dict = {}
                stats_dict['metrics.github.referrer.date'] = datetime.now()
                stats_dict['metrics.github.referrer.type'] = type
                stats_dict['metrics.github.referrer.org'] = org
                stats_dict['metrics.github.referrer.repo'] = repo
                stats_dict['metrics.github.referrer.referrer'] = item['referrer']
                stats_dict['metrics.github.referrer.count'] = item['count']
                stats_dict['metrics.github.referrer.uniques'] = item['uniques']

                # create output daily stats file
                with open('referrer_stats.csv', 'a') as f:
                    writer = csv.DictWriter(
                        f, fieldnames=['metrics.github.referrer.date',
                                       'metrics.github.referrer.type',
                                       'metrics.github.referrer.org',
                                       'metrics.github.referrer.repo',
                                       'metrics.github.referrer.referrer',
                                       'metrics.github.referrer.count',
                                       'metrics.github.referrer.uniques']
                    )
                    writer.writerow(stats_dict)


if __name__ == '__main__':
    cli()
