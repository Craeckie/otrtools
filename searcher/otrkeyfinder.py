import re, requests, os
from bs4 import BeautifulSoup
from datetime import timedelta
from multiprocessing.dummy import Pool
from functools import lru_cache
from itertools import chain, repeat

class Title:
    def __init__(self, title, length, items, isSimilarDecoded):
      self.title = title
      self.length = length
      self.items = items
      self.isSimilarDecoded = isSimilarDecoded

    def item_count(self):
      return len(self.items)

sortkeyfn = lambda t:t['title']

@lru_cache(maxsize=1)
def loadKeys():
    path = "otrkey_cache"
    keys = []
    if os.path.exists(path):
        with open(path, 'r') as f:
          lines = f.readlines()
          keys = set(
            l.split('#')[1].strip()
            for l in lines
            if '#' in l
          )
          names = set()
          for key in keys:
            m = re.search('(?P<name>[a-zA-Z0-9_-]+)_[0-9]{2}\.[0-9]{2}\.[0-9]{2}_[0-9]{2}-[0-9]{2}_[0-9A-Za-z-]+_[0-9]+_TVOON_DE[A-Za-z0-9.]+$', key)
            if m:
              name = m.group("name")
              print(name)
              names.add(name)
            else:
              print(f"Couldn't parse {key}!")


    print(f"Loading keys.. found {len(keys)} keys with {len(names)} names")
    return (keys, names)
def refreshKeys():
    loadKeys.cache_clear()

def toOTRName(name):
    return name \
      .replace(' ', '_') \
      .replace(':', ' ') \
      .replace('.', '_') \
      .replace('\'', '_')

@lru_cache(maxsize=1024)
def _getFiles(p, search):
    print(f"Retreiving page: {p} for search '{search}'")
    r = requests.get('https://otrkeyfinder.com/en/?search=%s&order=date-name&page=%s' % (search, p))
    b = BeautifulSoup(r.text, 'html.parser')
    spans = b.find_all('span', { 'class': 'file'})
    files = []
    if spans:
        files = [s.string for s in spans]
    return files


def parsePage(p, search, min_dur, key_names):
    titles = []
    files = _getFiles(p, search)
    (keys, names) = key_names
    print(f"{len(keys)}, {len(names)}")

    for f in files:
      m = re.match('(?P<title>[a-zA-Z0-9_-]+)_(?P<time>[0-9]{2}\.[0-9]{2}\.[0-9]{2}_[0-9]{2}-[0-9]{2})_(?P<sender>[^_]+)_(?P<length>[0-9]+)_TVOON_DE.(?P<format>[a-zA-Z0-9.]+)\.otrkey', f)
      if m:
        time = timedelta(minutes=int(m.group('length')))
        #print(time)
        if time >= timedelta(minutes=min_dur):
          title = m.group('title')
          isDecoded = f.replace('.otrkey', '') in keys
          isSimilarDecoded = title in names
          if 'Ziemlich' in title:
            print(title)
            print(isSimilarDecoded)

          #print(f"File: '{f}', isDecoded: {isDecoded}")
          titles.append({
            'title': title.replace('_', ' '),
            'length': time,
            'file': f,
            'isDecoded': isDecoded,
            'isSimilarDecoded': isSimilarDecoded
            })
          # print("Title: %s, Length: %s" % (title, time))
      else:
        print("Error parsing %s!" % f)
    return titles

def get_titles(search, page_start=0, page_num=20, min_dur=60):
    #print(f"Search: {search}, start: {page_start}, num: {page_num}")
    #for p in :
    key_names = loadKeys()
    pages = range(page_start*page_num + 1, (page_start + 1) * page_num + 1)
    with Pool(4) as p:
      titles = list(chain.from_iterable(p.starmap(parsePage, zip(pages, repeat(search.lower()), repeat(min_dur), repeat(key_names)))))
    titles.sort(key=sortkeyfn)
    return titles
