# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('file_process.views',
    url(r'^$', 'list', name='list'),
    url(r'^report/(?P<genomeanalysis_id>\d+)/$', 'report', name='report'),
    url(r'^commentary/(?P<variant_id>\d+)/$', 'commentary', name='commentary')
)
