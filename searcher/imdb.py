# coding: utf-8
from bs4 import BeautifulSoup
import requests

def get_episodes(imdb_url):
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
