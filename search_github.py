#!/usr/bin/env python
from __future__ import print_function
import json
import math
import subprocess
import time
import urllib2
import os

PAGE_SIZE = 100

def query(term, page):
    url = 'https://api.github.com/search/repositories?q={}&page={}&per_page={}'.format(term, page, PAGE_SIZE)
    data = urllib2.urlopen(url).read()
    return json.loads(data)

print('searching github')
data = query('pretty+kicad', page=1)
items = data['items'][:]

total = data['total_count']
pages = int(math.ceil(total / PAGE_SIZE))

for n in range(2, pages + 2):
    time.sleep(0.01)
    data = query('pretty+kicad', page=n)
    items += data['items']

print('found {} items'.format(len(items)))

for i,item in enumerate(items):
    name = item['full_name']
    print('{}: checking {}'.format(i, name))
    if name.endswith('.pretty') and not os.path.exists(name):
        cmd = ['git', 'submodule', 'add', item['ssh_url'], name]
        subprocess.call(cmd)
