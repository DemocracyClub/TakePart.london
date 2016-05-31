from django.views.generic import View, TemplateView
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance

from .utils import make_image
from .models import GeographImage
from register.models import Ward


def closest_image(point):
    distance_m = 20

    images = GeographImage.objects.exclude(dream_image=None)
    images = images.filter(location__distance_lt=(point, D(mi=10)))
    images = images.annotate(distance=Distance('location', point))
    images = images.order_by('distance').first()
    return images

class ShareImageHTMLView(TemplateView):
    template_name = "share_images/share_source.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ward = Ward.objects.get(gss=kwargs['gss'])
        context['background_image'] = closest_image(ward.area.centroid)
        context['ward'] = ward
        return context


class ShareImageMakerView(View):
    pass
    # Get the background image pk
    # Get the message
    # request.build_absolute_uri

