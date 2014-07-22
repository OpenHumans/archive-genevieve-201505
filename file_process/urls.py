# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('file_process.views',
    url(r'^list/$', 'list', name='list'),
)
