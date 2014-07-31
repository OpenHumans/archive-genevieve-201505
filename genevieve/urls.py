from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views

from .views import UserCreateView

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'genevieve.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    (r'^file_process/', include('file_process.urls')),

    url(r'^accounts/signup/$', UserCreateView.as_view()),
    url(r'^accounts/login/$', auth_views.login,
        {'template_name': 'login.html',
         'extra_context': {'next': '/file_process'}}, name='auth_login'),

) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

