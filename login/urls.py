# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('login.views',
    url(r'^$', 'home', name='home'),
    )
