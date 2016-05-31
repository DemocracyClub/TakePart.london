from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^(?P<gss>E\d+)$', views.ShareImageHTMLView.as_view()),
]
