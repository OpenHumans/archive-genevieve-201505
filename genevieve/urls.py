from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views

from .views import UserCreateView

admin.autodiscover()

urlpatterns = patterns(
    '',

    url(r'^admin/', include(admin.site.urls)),

    url(r'^file_process/', include('file_process.urls',
                                   namespace='file_process')),
    url(r'^genomes/', include('genomes.urls',
                              namespace='genomes')),

    url(r'^accounts/signup/$', UserCreateView.as_view()),
    url(r'^$',
        auth_views.login,
        {'template_name': 'home.html',
         'extra_context': {'next': '/file_process'}}, name='auth_login'),
    url(r'^accounts/logout/$', auth_views.logout, {'next_page': '/'},
        name='auth_logout'),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
