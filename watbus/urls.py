from django.conf.urls import patterns, url
from django.views.generic.base import RedirectView
from watbus import views

urlpatterns = patterns('',
        url(r'^$', views.coming, name='comingsoon'),
        url(r'^search/', views.search, name='search'),
        url(r'^map/$', views.map, name='map'),
        url(r'^browse/$', views.browse, name='browse'),
        url(r'^browse/stops/(?P<stop_id>.+)/$', views.browse_stops, name='browse'),
        url(r'^browse/trips/(?P<trip_id>.+)/$', views.browse_trips, name='browse'),
        url(r'^browse/frequent_stops/$', views.browse_all_freqstops, name='freqstop'),
        url(r'^browse/frequent_stop/(?P<stop_id>place_.+)/$', views.browse_freqstop, name='freqstop'),
        url(r'^stopjson$', views.stopjson, name='stopjson'),
        url(r'^about$', views.about, name='about'),
        url(r'^sitemap$', views.sitemap, name='sitemap')
)
