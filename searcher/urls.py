from django.urls import path
from django.conf.urls import include, url

from . import views

urlpatterns = [
    url(r'^index/', views.index, name='index'),
    url(r'^imdb_index/', views.imdb_index, name='imdb')
]
