from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.HomeView.as_view(), name="home_view"),
    url(r'^about/$', views.AboutView.as_view(), name="about_view"),
    url(r'^league_table/$', views.LeagueTables.as_view(), name="league_table"),
    url(r'^not_covered/$', views.NotCovered.as_view(), name="not_covered_view"),
    url(r'^postcode/(?P<postcode>[^/]+)$',
        views.PostcodeRedirectView.as_view(),
        name="postcode_view"),
    url(r'^ward/(?P<gss>E\d+)$',
        views.WardView.as_view(),
        name="ward_view"),
]
