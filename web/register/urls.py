from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^map/$', views.MapView.as_view(), name="map_view"),
    url(r'^map/api/$', views.MapAPIView.as_view(), name="map_api_view"),
]
