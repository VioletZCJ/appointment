from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib import admin

from django.contrib.auth.views import login, logout

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'appointment.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^$', 'appointment.views.home', name='home'),
    url(r'^add/$', 'appointment.views.add'),
    url(r'^update/$', 'appointment.views.update'),
    url(r'^delete/$', 'appointment.views.delete'),
    url(r'^admin/', include(admin.site.urls)),

    (r'^accounts/login/$',  login, {'template_name':'login.html'}),
    (r'^accounts/logout/$', logout),
)
urlpatterns += patterns('',
    (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_PATH}),
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
)