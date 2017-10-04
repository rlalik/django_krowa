# -*- coding: utf-8 -*-
from django.conf.urls import url
from .views import index, search_krowa_sequence

app_name="krowa"

urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'^search$', search_krowa_sequence, name='search'),
]
