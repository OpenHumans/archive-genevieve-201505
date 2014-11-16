# -*- coding: utf-8 -*-
"""URLs for genome reports and variant information"""
from django.conf.urls import patterns, url

from .views import GenomeAnalysesView, GenomeReportView


urlpatterns = patterns(
    '',
    url(r'^$', GenomeAnalysesView.as_view(), name='reports_list'),
    url(r'^report/(?P<pk>\d+)/$', GenomeReportView.as_view(),
        name='report'),
)
