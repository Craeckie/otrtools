# coding: utf-8
from django.shortcuts import render
from django.http import HttpResponse
import urllib.parse
from itertools import groupby
from datetime import timedelta

from .otrkeyfinder import Title, get_titles, refreshKeys, toOTRName
from .imdb import get_episodes

sortkeyfn = lambda t:t['title']

def group_titles(titles):
    res = []
    for k,values in groupby(titles, sortkeyfn):
        # print(k)
        values = list(values)
        isSimilarDecoded = any(x['isSimilarDecoded'] for x in values)
        if 'Ziemlich' in k:
          print(isSimilarDecoded)
        seconds = [x['length'].seconds for x in values]
        item_count = len(seconds)
        time = timedelta(seconds=sum(seconds) / item_count)

        res.append(Title(k, time, values, isSimilarDecoded)) #{'title': k, 'length': time, 'items':list(values)})
    return res

def index(request):
    q = request.GET.get('q', '_uk .hq')
    s = int(request.GET.get('s', '0'))
    num = int(request.GET.get('num', '20'))
    dur = int(request.GET.get('dur', '80'))
    refreshKeys()
    titles = get_titles(search=q, page_start=s, page_num=num, min_dur=dur)
    grouped = group_titles(titles)
    ctx = {
        'titles': grouped,
        'search': q
    }
    return render(request, 'searcher/index.html', ctx)

def imdb_index(request):
    url = request.GET.get('url')
    q = request.GET.get('q')
    episodes = []
    if url:
        episodes = get_episodes(url)
    if q:
        # titles = get_titles(search=q, page_start=0, page_num=50, min_dur=40)
        # grouped = group_titles(titles)
        refreshKeys()
        for e in episodes:
            title = toOTRName(e['title'])
            query = toOTRName(q)
            results = get_titles(search=f"{query} {title}", page_start=0, page_num=1, min_dur=40)
            e['otr'] = results
            e['decoded'] = any(r for r in results if r['isDecoded'])
            cur_url = e['url']
            e['url'] = urllib.parse.urljoin(url, cur_url)

            # for group in grouped:
            #     if title.lower() in group.title.lower():
            #         e['otr'] = group
            #         break

    ctx = {
        'episodes': episodes,
        'search': q
    }
    return render(request, 'searcher/imdb.html', ctx)
