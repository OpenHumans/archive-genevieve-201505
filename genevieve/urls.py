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
<<<<<<< HEAD
    url(r'^$', TemplateView.as_view(template_name='home.html'),
        name='home'),
=======
<<<<<<< HEAD
    url(r'^$', TemplateView.as_view(template_name='home.html'),
        name='home'),
=======
    url(r'^$', TemplateView.as_view(template_name='pages/home.html'),
        name='home'),
    url(r'^about/$', TemplateView.as_view(template_name='pages/about.html'),
        name='about'),
    url(r'^community_guidelines/$',
        TemplateView.as_view(template_name='pages/community_guidelines.html'),
        name='community_guidelines'),
    url(r'^contact-us/$',
        TemplateView.as_view(template_name='pages/contact_us.html'),
        name='contact_us'),
>>>>>>> c8757c2dbdefcc02dc41063b0fd4f8c43607fbc8
>>>>>>> dd197f87a63a14c0d388a12f3aa7db2ed2a88e34

    url(r'^admin/', include(admin.site.urls)),

    url(r'^file_process/', include('file_process.urls',
                                   namespace='file_process')),
    url(r'^genomes/', include('genomes.urls',
                              namespace='genomes')),

    url(r'^account/', include('account.urls')),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
