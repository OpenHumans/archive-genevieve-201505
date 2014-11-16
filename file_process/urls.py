# -*- coding: utf-8 -*-
"""URLs for genome reports and variant information"""
from django.conf.urls import patterns, url

from .views import GenomeAnalysesView, GenomeImportView, GenomeReportView

from .views import receive_23andme, complete_23andme, commentary

urlpatterns = patterns(
    '',
    url(r'^$', GenomeAnalysesView.as_view(), name='list_reports'),
    url(r'^genome_import/?$', GenomeImportView.as_view(),
        name='genome_import'),
    url(r'^report/(?P<pk>\d+)/$', GenomeReportView.as_view(),
        name='report'),
    url(r'^commentary/(?P<variant_id>\d+)/$', commentary, name='commentary'),
    url(r'^receive_23andme/?', receive_23andme, name='receive_23andme'),
    url(r'^complete_23andme/?', complete_23andme, name='complete_23andme')
)
