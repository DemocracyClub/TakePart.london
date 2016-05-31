from django.conf.urls import include, url
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    url(r'', include('yournumber.urls')),
    url(r'share/', include('share_images.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
