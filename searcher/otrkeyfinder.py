import re, requests, os
import urllib

from bs4 import BeautifulSoup
from datetime import timedelta
from multiprocessing.dummy import Pool
from functools import lru_cache
from itertools import chain, repeat
from operator import itemgetter
from django.conf import settings

class Title:
    def __init__(self, title, length, items, isSimilarDecoded, num):
      self.title = title
      self.length = length
      self.items = items
      self.isSimilarDecoded = isSimilarDecoded
      self.num = num

    def item_count(self):
      return len(self.items)

@lru_cache(maxsize=1)
def loadKeys():
    path = settings.OTRKEY_CACHE
    keys = []
    names = set()
    if os.path.exists(path):
        print(f"Importing keys from {path}")
        with open(path, 'r') as f:
          lines = f.readlines()
          keys = set(
            l.split('#')[1].strip()
            for l in lines
            if '#' in l
          )
          for key in keys:
            m = re.search('(?P<name>[a-zA-Z0-9_-]+)_[0-9]{2}\.[0-9]{2}\.[0-9]{2}_[0-9]{2}-[0-9]{2}_[0-9A-Za-z-]+_[0-9]+_TVOON_DE[A-Za-z0-9.]+$', key)
            if m:
              name = m.group("name")
              # print(name)
              names.add(name)
            else:
              print(f"Couldn't parse {key}!")


    print(f"Loading keys.. found {len(keys)} keys with {len(names)} names")
    return (keys, list(names))
def refreshKeys():
    loadKeys.cache_clear()

def toOTRName(name):
    name = name \
      .replace(' ', '_') \
      .replace('&', ' ') \
      .replace('ä', '__') \
      .replace('ö', '__') \
      .replace('ü', '__') \
      .replace(':', ' ') \
      .replace('.', '_') \
      .replace('\'', '_') \
      .replace(', ', '_') \
      .replace(',', ' ') \
      .replace('/', ' ')
      # .replace('-', ' ') \

    return re.sub('[^a-zA-Z0-9 _-]+', '', name)

def parseOtrkeys(otrkey_divs):
    files = []
    for otrkey_div in otrkey_divs:
        file_spans = otrkey_div.find_all('span', { 'class': 'file' })
        if len(file_spans) > 0:
            file = file_spans[0].string
            mirrors = []
            mirror_divs = otrkey_div.find_all('div', { 'class': 'mirror' })
            for mirror_div in mirror_divs:
                mirror = {}
                links = mirror_div.find_all('a', { 'target': '_blank' })
                if len(links) > 0:
                    link = links[0]
                    name = link.string
                    url = link.attrs['href']
                    if not url.startswith('https://'):
                        url = urllib.parse.urljoin('https://otrkeyfinder.com/', url)

                    mirror = {
                      'name':     name.strip(),
                      'link':     url.strip(),
                      'priority': settings.MIRROR_PRIORITIES.index(name) if name in settings.MIRROR_PRIORITIES else len(settings.MIRROR_PRIORITIES)
                    }
                else:
                    print(f"Error: couldn't find a link in {mirror_div}")
                if mirror:
                    mirrors.append(mirror)
            if mirrors:
                files.append({
                    'file': file.strip(),
                    'mirrors': sorted(mirrors, key=itemgetter('priority', 'name')),
                })
        else:
            print(f"Error: couldn't find a 'file' span in {otrkey_div}")
    return files

format_name = {
  'mpg.mp4' : 'MP4',
  'mpg.avi' : 'AVI',
  'mpg.HQ.avi' : 'HQ',
  'mpg.HD.avi' : 'HD',
  'mpg.HD.ac3' : 'AC3',
}

def parseTitles(otrkeys, min_dur, key_names):
    titles = []
    (keys, names) = key_names
    # print(f"{len(keys)}, {len(names)}")

    for otrkey in otrkeys:
      file = otrkey['file']
      file_decrypted = re.sub('\.otrkey$', '', file)
      m = re.match('(?P<title>[a-zA-Z0-9_-]+)_(?P<time>[0-9]{2}\.[0-9]{2}\.[0-9]{2}_[0-9]{2}-[0-9]{2})_(?P<sender>[^_]+)_(?P<length>[0-9]+)_TVOON_DE.(?P<format>[a-zA-Z0-9.]+)\.otrkey', file)
      if m:
        time = timedelta(minutes=int(m.group('length')))
        #print(time)
        if time >= timedelta(minutes=min_dur):
          title = m.group('title')
          format = m.group('format')
          if format in format_name:
              format = format_name[format]
          isDecoded = file.replace('.otrkey', '') in keys
          isSimilarDecoded = title in names

          mirrors = otrkey['mirrors']
          if len(mirrors) == 0:
            continue

          chosen_mirror = mirrors[0]
          found_mirror = False
          for priority in settings.MIRROR_PRIORITIES:
              for mirror in mirrors:
                  if mirror == mirror['name']:
                      found_mirror = True
                      chosen_mirror = mirror
                      break
              if found_mirror:
                  break

          #print(f"File: '{f}', isDecoded: {isDecoded}")
          titles.append({
            'title': title.replace('_', ' '),
            'length': time,
            'file': file,
            'file_decrypted': file_decrypted,
            'mirrors': mirrors,
            'num_mirrors': len(mirrors),
            'chosen_mirror': chosen_mirror,
            'format': format,
            'isDecoded': isDecoded,
            'isSimilarDecoded': isSimilarDecoded,
            'priority': settings.FORMAT_PRIORITIES.index(format) if format in settings.FORMAT_PRIORITIES else len(settings.FORMAT_PRIORITIES)
            })

      else:
        print("Error parsing %s!" % file)
    titles = sorted(titles, key=itemgetter('priority'))
    titles = sorted(titles, key=itemgetter('num_mirrors'), reverse=True)
    return titles

@lru_cache(maxsize=1024)
def getTitles(
    search,
    page_start=1,
    page_num=20,
    min_dur=60,
    isFirstPage=True,
    key_names=None):

    if not key_names:
      key_names = loadKeys()

    print(f"Retreiving page: {page_start} for search '{search}'")
    r = requests.get('https://otrkeyfinder.com/en/?search=%s&order=date-name&page=%s' % (search, page_start))
    b = BeautifulSoup(r.text, 'html.parser')

    otrkey_divs = b.find_all('div', { 'class': 'otrkey'})
    files = parseOtrkeys(otrkey_divs)

    titles = parseTitles(files, min_dur, key_names)
    if isFirstPage:
        key_names = loadKeys()
        last_page_num = 0

        last_page_li = b.find('li', { 'class': 'last'})
        if last_page_li:  # has any pages?
            last_page_link = last_page_li.a.attrs['href']
            m = re.search('page=([0-9]+)', last_page_link)
            if not m:
                print('Couldn\'t parse last page number from ' + last_page_link)
            last_page_num = int(m.group(1))
            # print(f"Last page: {last_page_num}")
            first_page = min(page_start, last_page_num)
            # print(f"last_page: {page_start} * {page_num} + 1")
            last_page = min(page_start + page_num - 1, last_page_num + 1)
            # print(f"Page range: {first_page} -> {last_page}")
            pages = range(first_page, last_page + 1)
            with Pool(4) as p:
              titles.extend(chain.from_iterable(p.starmap(getTitles, zip(
                  repeat(search.lower()),
                  pages,
                  repeat(page_num),
                  repeat(min_dur),
                  repeat(False),
              ))))
        titles.sort(key=itemgetter('title'))
    print(f"{page_start}: Found {len(titles)} titles!")
    return titles
