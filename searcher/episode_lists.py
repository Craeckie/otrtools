# coding: utf-8
import requests, re
from bs4 import BeautifulSoup
from django.conf import settings
from .otrkeyfinder import toOTRName
from datetime import datetime
from difflib import SequenceMatcher

def get_episodes(website, url, series, german=False, otrNameFormat=None):
    if website == 'IM':
        episodes = imdb_episodes(url, series)
    elif website == 'SJ':
        episodes = serienjunkie_episodes(url, series, german)
    else:
        raise ValueError(f'Invalid website for episode lists: {website}')
    for e in episodes:
        episode = e['episode']
        season = e['season']
        title = e['title']
        e.update({
          'series': series,
          'title': title,
          'OTRseries': toOTRName(series),
          'OTRtitle': toOTRName(title),
          'extension': settings.DEST_EXT,
        })
        format = settings.SERIES_NAME_FORMAT
        e['destName'] = format.format(**e) \
            if episode >= 0 and season >=0 else None
        e['search'] = otrNameFormat.format(**e) \
            if otrNameFormat else "{OTRseries} {OTRtitle}".format(**e)
    return episodes

def imdb_episodes(imdb_url, series):
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
          })
        else:
            print("Found no info for %s" % item)

    return episodes

# https://www.serienjunkies.de/lethal-weapon/alle-serien-staffeln.html
def serienjunkie_episodes(url, series, german=True):
    r = requests.get(url)
    b = BeautifulSoup(r.text, 'html.parser')
    table = b.find("table", attrs={'class': 'eplist'})
    if not table:
       raise LookupError(f"Couldn't find episode list of serienjunkies.de at {url}")
    episodes = []
    for row in table.find_all('tr'):
        cols = row.find_all('td', attrs={'class': ['e0', 'e1']})
        if len(cols) >= 4:
            season_str = cols[0].get_text()
            season = episode = -1
            m = re.match('([0-9]+)x([0-9]+)', season_str)
            if m:
                season = int(m.group(1))
                episode = int(m.group(2))
            else:
                raise LookupError(f"Couldn't match number of episode and season in {season_str}!")

            title = title_link = None
            if german:
                col = cols[3]
                title_link = col.find('a')
                if not title_link:
                    raise LookupError(f"Couldn't find title link on serienjunkies.de in {col}")
                title = title_link.get_text()
            else:
                col = cols[2]
                title_link = col.find('a', attrs={'itemprop': 'url'})
                if not title_link:
                    raise LookupError(f"Couldn't find title link on serienjunkies.de in {col}")
                title_span = col.find('span', attrs={'itemprop': 'name'})
                if not title_span:
                    raise LookupError(f"Couldn't find title span on serienjunkies.de int {col}")
                title = title_span.get_text()
            url = title_link.attrs['href']

            date_col = row.find('td', attrs={'class': 'ar'})
            date = None
            if date_col:
                date_str = date_col.get_text()
                if date_str:
                    date = datetime.strptime(date_str, "%d.%m.%Y")

            episodes.append({
              'title': title,
              'url': url,
              'season': season,
              'episode': episode,
              'date': date,
            });
    # Ugly workaround for wrong numbering in case of double episodes (two in one)
    print(f"Length: {len(episodes)}")
    i = 0
    while i < len(episodes) - 1:
        e = episodes[i]
        next = episodes[i + 1]
        if e['season'] == next['season'] and e['date'] == next['date']:
            firstTitle = e['title']
            nextTitle = next['title']
            match = SequenceMatcher(None, firstTitle, nextTitle).find_longest_match(
                0,
                len(firstTitle),
                0,
                len(nextTitle))
            # Both titles start with the same string
            if match and match.a == 0 and match.b == 0:
                e['title'] = firstTitle[:match.size]

            episodes.remove(next)
            for j in range(i + 1, len(episodes)):
                e2 = episodes[j]
                if e2['season'] == e['season']:
                    e2['episode'] -= 1
                else:
                    break
        i += 1
    return episodes
