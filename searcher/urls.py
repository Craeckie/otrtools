from django.urls import path
from django.conf.urls import include, url
from django.views.generic import RedirectView

from . import views

app_name = 'searcher'

urlpatterns = [
    url(r'^movies/', views.MovieView.as_view(), name='movies'),
    url(r'^series/', views.SeriesView.as_view(), name='series'),
    path('cutlist/<str:file>/', views.cutlist, name='cutlist'),
    path('cutlist_test/', views.cutlist_test, name='cutlist-test'),
    path('clearCache/', views.clearCache, name='clear-cache'),
    path('', RedirectView.as_view(pattern_name=f'{app_name}:movies', permanent=False), name='main'),
]
