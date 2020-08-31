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

import click
import requests


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
@click.option("-o", "--org", help="github org", type=str, default='PaloAltoNetworks')
@click.option("-r", "--repo", help="github repo", type=str, default='')
def cli(git_auth_token, org, repo):
    """
    grab github traffic stats and generate csv output
    :param git_token: personal auth token used for API access
    :param org: github org
    :param repo: github repo
    :return: None
    """

    print(f'\npulling data for {org}/{repo}')
    # get views and clones traffic stats
    for type in ['views', 'clones']:
        # get and output traffic data
        print(f'\n  {type}')
        repo_traffic = git_api_query_traffic(git_auth_token, org, repo, type)
        print(f"  14-day count: {repo_traffic['count']}")
        print(f"  14-day unique: {repo_traffic['uniques']}")
        print('  daily counts (date, count, unique)')
        for item in repo_traffic[type]:
            print(f"    {item['timestamp']}, {item['count']}, {item['uniques']}")

    # get referrers traffic stats
    print('\n  Top Referrers (referrer, count, unique')
    repo_traffic = git_api_query_traffic(git_auth_token, org, repo, 'popular/referrers')

    for item in repo_traffic:
        print(f"    {item['referrer']}, {item['count']}, {item['uniques']}")


if __name__ == '__main__':
    cli()
