# -*- coding: utf-8 -*-
"""URLs for genome reports and variant information"""
from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns(
    'file_process.views',
    url(r'^$', 'list_reports', name='list_reports'),
    url(r'^report/(?P<genomeanalysis_id>\d+)/$', 'report', name='report'),
    url(r'^commentary/(?P<variant_id>\d+)/$', 'commentary', name='commentary'),
    url(r'^receive_23andme/?', 'receive_23andme', name='receive_23andme'),
    url(r'^complete_23andme/?', 'complete_23andme', name='complete_23andme')
)
