from django.urls import path
from django.conf.urls import include, url

from . import views

app_name = 'searcher'

urlpatterns = [
    url(r'^index/', views.index, name='index'),
    url(r'^imdb_index/', views.imdb_index, name='imdb'),
    path('cutlist/<str:file>/', views.cutlist, name='cutlist'),
    path('cutlist_test/', views.cutlist_test, name='cutlist-test'),
]
