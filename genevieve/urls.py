from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views

from .views import UserCreateView
from django.core.urlresolvers import reverse_lazy
from django.views.generic import TemplateView

admin.autodiscover()

urlpatterns = patterns(
    '',

    #simple pages
    url(r'^$', TemplateView.as_view(template_name='home.html'),

    url(r'^admin/', include(admin.site.urls)),

    url(r'^file_process/', include('file_process.urls',
                                   namespace='file_process')),
    url(r'^genomes/', include('genomes.urls',
                              namespace='genomes')),

    url(r'^account/', include('account.urls')),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
