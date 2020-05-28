from django.urls import path
from django.conf.urls import include, url

from . import views

app_name = 'downloader'

urlpatterns = [
    url(r'^add/direct/', views.startRequest, name='add-direct'),
    url(r'^add/', views.AddView.as_view(), name='add'),
    url(r'^downloads/', views.DownloadsView.as_view(), name='downloads'),
]
