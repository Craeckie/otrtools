# coding: utf-8
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import urllib.parse, requests
from itertools import groupby
from datetime import timedelta
from operator import itemgetter, attrgetter

from .otrkeyfinder import Title, get_titles, refreshKeys, toOTRName
from .episode_lists import get_episodes
from .forms import MovieIndexForm, SeriesIndexForm

sortkeyfn = lambda t:t['title']

def group_titles(titles):
    res = []
    num = 0;
    for k,values in groupby(titles, sortkeyfn):
        # print(k)
        values = list(values)
        for i in range(0, len(values)):
            values[i]['num'] = i
        isSimilarDecoded = any(x['isSimilarDecoded'] for x in values)
        if 'Ziemlich' in k:
          print(isSimilarDecoded)
        seconds = [x['length'].seconds for x in values]
        item_count = len(seconds)
        time = timedelta(seconds=sum(seconds) / item_count)

        res.append(Title(k, time, values, isSimilarDecoded, num)) #{'title': k, 'length': time, 'items':list(values)})
    return res

def index(request):
    grouped = []
    if request.method == 'POST':
        form = MovieIndexForm(request.POST)
        if form.is_valid():
            query = form.cleaned_data.get("query")
            min_duration = form.cleaned_data.get('min_duration')
            max_page = form.cleaned_data.get("max_page")
            start_page = form.cleaned_data.get("start_page")

            refreshKeys()
            titles = get_titles(
                search=query,
                page_start=start_page,
                page_num=max_page,
                min_dur=min_duration)
            grouped = group_titles(titles)
    else:
        form = MovieIndexForm()
    ctx = {
        'titles': grouped,
        'form': form,
    }
    return render(request, 'searcher/index.html', ctx)

def imdb_index(request):
    episodes = []

    if request.method == 'POST':
        form = SeriesIndexForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data.get("url")
            website = form.cleaned_data.get('website')
            series = form.cleaned_data.get("series")

            # titles = get_titles(search=q, page_start=0, page_num=50, min_dur=40)
            # grouped = group_titles(titles)
            episodes = get_episodes(website, url)
            refreshKeys()
            for e in episodes:
                title = toOTRName(e['title'])
                query = toOTRName(series)
                results = get_titles(search=f"{query} {title}", page_start=0, page_num=1, min_dur=40)
                e['otr'] = results
                e['decoded'] = any(r for r in results if r['isDecoded'])
                cur_url = e['url']
                e['url'] = urllib.parse.urljoin(url, cur_url)

                # for group in grouped:
                #     if title.lower() in group.title.lower():
                #         e['otr'] = group
                #         break
    else:
        form = SeriesIndexForm()
    ctx = {
        'episodes': episodes,
        'form': form
    }
    return render(request, 'searcher/imdb.html', ctx)

def cutlist_test(request):
    return render(request, 'searcher/cutlists.html', {})
def cutlist(request, file):
  # json = {'items': [{'id': 322848,
  #    'name': 'Lethal Weapon  Best Buds',
  #    'airDate': '2016-10-05T20:00:00+02:00',
  #    'uploadDate': '2016-10-08T22:25:06+02:00',
  #    'otrkey': 'Lethal_Weapon__Best_Buds_16.10.05_20-00_uswnyw_60_TVOON_DE.mpg.HQ.avi',
  #    'comment': 'inkl. Vorschau, cut with Super OTR (Super OTR 0.9.6.0b79)',
  #    'suggestedName': 'Lethal Weapon - S01E03 - Best Buds',
  #    'channel': 'uswnyw',
  #    'author': 'Hummel',
  #    'rating': {'avg': '0.00', 'n': 0, 'author': 5},
  #    'hits': 2,
  #    'duration': '00:43:20',
  #    'quality': 'hq',
  #    'cutCount': 6,
  #    'errors': {'start': False,
  #     'end': False,
  #     'video': False,
  #     'audio': False,
  #     'other': False,
  #     'epg': False,
  #     'epgDesc': None,
  #     'otherDesc': None},
  #    '_my': {'canRate': True}},
  #   {'id': 324225,
  #    'name': 'Lethal Weapon  Best Buds',
  #    'airDate': '2016-10-05T20:00:00+02:00',
  #    'uploadDate': '2016-10-06T23:32:15+02:00',
  #    'otrkey': 'Lethal_Weapon__Best_Buds_16.10.05_20-00_uswnyw_60_TVOON_DE.mpg.HQ.avi',
  #    'comment': None,
  #    'suggestedName': 'Lethal Weapon - S01E03 - Best Buds - HQ',
  #    'channel': 'uswnyw',
  #    'author': 'katteld1',
  #    'rating': {'avg': '5.00', 'n': 3, 'author': 5},
  #    'hits': 46,
  #    'duration': '00:42:56',
  #    'quality': 'hq',
  #    'cutCount': 6,
  #    'errors': {'start': False,
  #     'end': False,
  #     'video': False,
  #     'audio': False,
  #     'other': False,
  #     'epg': False,
  #     'epgDesc': None,
  #     'otherDesc': None},
  #    '_my': {'canRate': True}}],
  #    'hasMore': False,
  #    'currentPage': 0}
    data = '{"conds":[{"query":"%s","field":"name"}],"isOrConnection":false,"sortBy":"datebroadcast","isAsc":true,"page":0}' % file
    print(data)
    resp = requests.post('http://www.cutlist.at/api/search-by', data=data)
    json = resp.json()
    print(json)
    items = [dict(item) for item in json['items']]
    items = sorted(items, key=itemgetter('hits'), reverse=True)
    items = sorted(items, key=lambda item: item['rating']['avg'] * min(5, item['rating']['n']), reverse=True)
    print(items)
    # return JsonResponse(resp.json())
    return JsonResponse({'items': items})
