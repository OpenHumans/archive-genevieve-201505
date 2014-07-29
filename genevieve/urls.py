from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import RedirectView

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'genevieve.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    (r'^file_process/', include('file_process.urls')),
)
