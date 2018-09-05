from django.urls import path
from django.conf.urls import include, url

from . import views

app_name = 'downloader'

urlpatterns = [
    url(r'^add/', views.add, name='add'),
]
