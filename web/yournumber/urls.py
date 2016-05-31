from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.HomeView.as_view(), name="home_view"),
    url(r'^league_table/$', views.LeagueTables.as_view(), name="league_table"),
    url(r'^postcode/(?P<postcode>[^/]+)$',
        views.PostcodeView.as_view(),
        name="postcode_view"),
]
