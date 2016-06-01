import requests

from django.views.generic import TemplateView, FormView, RedirectView
from django.core.urlresolvers import reverse

from register.models import RegisteredPerson, Ward, Borough

from .forms import PostcodeLookupForm


class AreaNotCoveredError(ValueError):
    pass


class BaseDataView(object):

    def get_data_for_postcode(self, postcode):
        data = {}
        area_info = RegisteredPerson.objects.filter(postcode=postcode).first()
        if area_info:
            data['ward'] = area_info.ward
            data['borough'] = area_info.borough
        else:
            req = requests.get(
                "http://mapit.democracyclub.org.uk/postcode/{}".format(
                    postcode
                ))
            for area_id, area in req.json()['areas'].items():
                if area['type'] == "LBW":
                    data['ward'] = Ward.objects.get(gss=area['codes']['gss'])
                    data['borough'] = data['ward'].borough
        if 'ward' not in data:
            raise AreaNotCoveredError
        return data

    def get_data_for_gss(self, gss):
        data = {}
        try:
            data['ward'] = Ward.objects.get(gss=gss)
            data['borough'] = data['ward'].borough
            return data
        except Ward.DoesNotExist:
            raise AreaNotCoveredError()


class PostcodeRedirectView(BaseDataView, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        postcode = self.kwargs['postcode']
        try:
            data = self.get_data_for_postcode(postcode)
            if 'ward' in data:
                return reverse('ward_view', kwargs={'gss': data['ward'].gss})
        except AreaNotCoveredError:
            return reverse('not_covered_view')


class AboutView(TemplateView):
    template_name = "about.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hide_content_block'] = True
        return context


class HomeView(FormView):
    template_name = "home.html"
    form_class = PostcodeLookupForm

    def get_initial(self):
        initial = self.initial.copy()
        if 'invalid_postcode' in self.request.GET:
            initial['postcode'] = self.request.GET.get('postcode')
        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'autofocus': True})
        return kwargs

    def form_valid(self, form):
        postcode = form.cleaned_data['postcode']
        self.success_url = reverse(
            'postcode_view',
            kwargs={'postcode': postcode}
        )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hide_content_block'] = True
        return context


class WardView(BaseDataView, TemplateView):
    template_name = "ward.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        gss = self.kwargs['gss']
        context['area_info'] = self.get_data_for_gss(gss)
        return context

class LeagueTables(TemplateView):
    template_name = "league_table.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        ward_data = Ward.objects.all().filter(percent_registered__gt=40)
        ward_data = ward_data.order_by('percent_registered')
        ward_data = ward_data.select_related('borough')


        context['ward_data'] = ward_data
        return context


class NotCovered(TemplateView):
    template_name = "not_covered.html"
