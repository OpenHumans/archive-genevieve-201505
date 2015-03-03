# -*- coding: utf-8 -*-
"""URLs for genome reports and variant information"""
from django.conf.urls import patterns, url

from .views import (GenomeAnalysesView, GenomeReportView,
                    GenomeReportJSONView, ReportsJSON)

urlpatterns = patterns(
    '',
    url(r'^$', GenomeAnalysesView.as_view(), name='reports_list'),
    url(r'^report/(?P<pk>\d+)/$', GenomeReportView.as_view(),
        name='report'),
    url(r'^report/(?P<pk>\d+)/json$', GenomeReportJSONView.as_view(),
        name='report-json'),
    url(r'get-reports/$', ReportsJSON.as_view(), name='get-reports'),
)
