from django.urls import path
from django.conf.urls import include, url

from . import views

app_name = 'searcher'

urlpatterns = [
    url(r'^movies/', views.MovieView.as_view(), name='movies'),
    url(r'^series/', views.SeriesView.as_view(), name='series'),
    path('cutlist/<str:file>/', views.cutlist, name='cutlist'),
    path('cutlist_test/', views.cutlist_test, name='cutlist-test'),
]
