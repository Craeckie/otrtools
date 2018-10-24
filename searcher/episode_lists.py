# coding: utf-8
from bs4 import BeautifulSoup
import requests

def get_episodes(website, url):
    if website == 'IM':
        return imdb_episodes(url)
    elif website == 'SJ':
        return serienjunkie_episodes(url)
    else:
        raise ValueError(f'Invalid website for episode lists: {website}')

def imdb_episodes(imdb_url):
    r = requests.get(imdb_url)
    b = BeautifulSoup(r.text, 'html.parser')
    l = b.find_all("div", attrs={'class': 'list_item'})
    episodes = []
    for item in l:
        infos = item.find_all("div", attrs={'class':'info'})
        if len(infos) > 0:
            info = infos[0]
            s = info.strong
            url = s.a.attrs['href']
            episodes.append({
              'title': s.get_text(),
              'url': url
            })
        else:
            print("Found no info for %s" % item)

    return episodes

# https://www.serienjunkies.de/lethal-weapon/alle-serien-staffeln.html
def serienjunkie_episodes(url):
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
