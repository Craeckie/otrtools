from django.urls import path
from django.conf.urls import include, url
from django.views.generic import RedirectView

from . import views

app_name = 'searcher'

urlpatterns = [
    path('movies/', views.MovieView.as_view(), name='movies'),
    path('movies/<str:name>/', views.MovieView.as_view(), name='movies-search'),
    path('series/', views.SeriesView.as_view(), name='series'),
    path('series/add/', views.SeriesAddView.as_view(), name='series-add'),
    path('series/<int:series>/<int:season>/', views.SeriesView.as_view(), name='series'),
    path('cutlist/<str:file>/', views.cutlist, name='cutlist'),
    path('cutlist_test/', views.cutlist_test, name='cutlist-test'),
    path('clearCache/', views.clearCache, name='clear-cache'),
    path('', RedirectView.as_view(pattern_name=f'{app_name}:movies', permanent=False), name='main'),
]
