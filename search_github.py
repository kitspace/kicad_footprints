#!/usr/bin/env python
import urllib2
import json
import math
import time

PAGE_SIZE = 100

def query(term, page):
    url = "https://api.github.com/search/repositories?q={}&page={}&per_page={}".format(term, page, PAGE_SIZE)
    data = urllib2.urlopen(url).read()
    return json.loads(data)


data = query('pretty+kicad', page=1)
items = data['items'][:]

total = data['total_count']
print(total)
pages = int(math.ceil(total / PAGE_SIZE))

for n in range(2, pages + 2):
    time.sleep(0.1)
    print(n)
    data = query('pretty+kicad', page=n)
    items += data['items']

