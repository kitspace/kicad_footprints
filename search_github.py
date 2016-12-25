from __future__ import print_function
import json
import math
import subprocess
import time
import urllib2
import os

PAGE_SIZE = 100
TERM = 'pretty+kicad'

def query(term, page):
    url = 'https://api.github.com/search/repositories?q={}&page={}&per_page={}'.format(term, page, PAGE_SIZE)
    data = urllib2.urlopen(url).read()
    return json.loads(data)

print('searching github for "{}"'.format(TERM))
data = query(TERM, page=1)
items = data['items']

total = data['total_count']
pages = int(math.ceil(total / PAGE_SIZE))

for n in range(2, pages + 2):
    time.sleep(0.01)
    data = query(TERM, page=n)
    items += data['items']

print('found {} items'.format(len(items)))

for i,item in enumerate(items):
    name = item['full_name']
    if not os.path.exists(name):
        if name.endswith('.pretty'):
            print('adding {}'.format(name))
            cmd = ['git', 'submodule', 'add', item['html_url'], name]
            subprocess.call(cmd)
        else:
            print('ignoring {}'.format(name))
