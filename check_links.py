#!/usr/bin/env -S uv run
# checks that all links in the paper yaml are reachable
# deps (pyyaml, requests) are declared inline below; uv provisions them
# automatically the first time you run this script.

# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "pyyaml>=6.0.2",
#     "requests>=2.32.3",
# ]
# ///

import requests
import urllib3
import yaml

# the parnas1972 paper is throwing cert errors and I can't find another link for it.
# so requesting with verify=False and disabling warnings for now
urllib3.disable_warnings()


HEADERS = {'User-Agent': 'My User Agent 1.0'}
TIMEOUT = 20  # seconds per request; a hung host won't stall the whole run
TRANSIENT = (
    requests.exceptions.ConnectionError,
    requests.exceptions.Timeout,
    requests.exceptions.ChunkedEncodingError,
)


def fetch(link):
    """HEAD the link, fall back to GET on 405. Retry once on transient errors."""
    for attempt in (1, 2):
        try:
            response = requests.head(link, headers=HEADERS, verify=False, timeout=TIMEOUT,
                                     allow_redirects=True)
            if response.status_code == 405:
                response = requests.get(link, headers=HEADERS, verify=False, timeout=TIMEOUT,
                                       stream=True)
            return response
        except TRANSIENT as e:
            if attempt == 2:
                raise
            last = e
    raise last  # unreachable; keeps linters calm


with open('papers.yml') as file_:
    papers = yaml.safe_load(file_)

for paper in list(papers):
    papers += paper.get('related', [])


exit_code = 0
for paper in papers:
    ref = paper['author'].replace(',', '').split(' ')[0] + str(paper['year'])
    print(f'{ref}...', end='', flush=True)

    if '.acm.org/' in paper['link']:
        # the acm library (which has the majority of the paper links)
        # is now denying requests without javascript enabled
        # I'm skipping them since it's better to assume they work and check the rest
        # than removing this script or trying to find alternative sources for all the papers
        print('skipping ACM')
        continue

    try:
        response = fetch(paper['link'])
    except requests.exceptions.RequestException as e:
        exit_code = 1
        print(f' ERROR ({type(e).__name__})')
        print(f'    failed fetching {paper["link"]}')
        continue

    if response.ok:
        print('ok')
    else:
        exit_code = 1
        print(f' ERROR ({response.status_code})')
        print(f'    failed fetching {paper["link"]}')

exit(exit_code)
