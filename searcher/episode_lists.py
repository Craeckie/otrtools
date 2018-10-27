# coding: utf-8
import requests, re
from bs4 import BeautifulSoup
from django.conf import settings

def get_episodes(website, url, name):
    if website == 'IM':
        return imdb_episodes(url, name)
    elif website == 'SJ':
        return serienjunkie_episodes(url, name)
    else:
        raise ValueError(f'Invalid website for episode lists: {website}')

def imdb_episodes(imdb_url, name):
    r = requests.get(imdb_url)
    b = BeautifulSoup(r.text, 'html.parser')
    l = b.find_all("div", attrs={'class': 'list_item'})
    episodes = []
    for item in l:
        info = item.find("div", attrs={'class':'info'})
        image_div = item.find('div', attrs={'class':'image'})
        if info and image_div:
          s = info.strong
          url = s.a.attrs['href']
          title = s.get_text()
          episode_div = image_div.a.div.div
          episode_text = episode_div.get_text()
          m = re.match('S([0-9]+), Ep([0-9]+)', episode_text)
          episode = -1
          season = -1
          if m:
              season = int(m.group(1))
              episode = int(m.group(2))
          else:
              print("Couldn't parse season/episode for %s" % item)

          episodes.append({
            'title': title,
            'url': url,
            'season': season,
            'episode': episode,
            'destName': settings.SERIES_NAME_FORMAT.format(
              name=name, season=season, episode=episode, title=title, extension=settings.DEST_EXT
            ) if episode >= 0 and season >=0 else None,
          })
        else:
            print("Found no info for %s" % item)

    return episodes

# https://www.serienjunkies.de/lethal-weapon/alle-serien-staffeln.html
def serienjunkie_episodes(url, name):
    r = requests.get(url)
    b = BeautifulSoup(r.text, 'html.parser')
    tables = b.find_all("table", attrs={'class': 'eplist'})
    if len(tables) == 0:
       raise LookupError(f"Couldn't find episode list of serienjunkies.de at {url}")
    episodes = []
    for row in t.find_all('tr'):
        cols = row.find_all('td', attrs={'class': 'e0'})
        if len(cols) >= 4:
            title_link = cols[2].find_all('a', attrs={'itemprop', 'url'})[0]
            title_span = title_link.find_all('span', attrs={'itemprop', 'name'})
            season_str = cols[0].get_text()
            season = episode = -1
            m = re.match('([0-9]+)x([0-9]+)', season_str)
            if m:
                season = int(m.group(1))
                episode = int(m.group(2))
            episodes.append({
              'title': title_span.get_text(),
              'url': title_link.attrs['href'],
              'season': season,
              'episode': episode,
            });
    return episodes
