from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.HomeView.as_view(), name="home_view"),
    url(r'^postcode/(?P<postcode>[^/]+)$',
        views.PostcodeView.as_view(),
        name="postcode_view"),
]
