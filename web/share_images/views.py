from django.views.generic import View, TemplateView

from .utils import make_image


class ShareImageHTMLView(TemplateView):
    template_name = "share_images/share_source.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class ShareImageMakerView(View):
    pass
    # Get the background image pk
    # Get the message
    # request.build_absolute_uri

