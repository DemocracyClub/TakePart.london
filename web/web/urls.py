from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'', include('yournumber.urls')),
    url(r'share/', include('share_images.urls')),
]
