from django.contrib.auth.decorators import login_required
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic import View
from django.utils.decorators import method_decorator

from variants.models import Variant, ClinVarRecord
from .models import GenomeAnalysis, GenomeAnalysisVariant
from .models import GenomeAnalysis
import json
from django.http import HttpResponse
from django.core import serializers


class GenomeAnalysesView(ListView):

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(GenomeAnalysesView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        genome_analyses = GenomeAnalysis.objects.filter(user=self.request.user)
        return genome_analyses


class GenomeReportView(DetailView):
    model = GenomeAnalysis

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(GenomeReportView, self).dispatch(*args, **kwargs)


class BaseJSONDataView(View):
    """Base view for returning JSON data.
    Additional definitions needed:
      - get_data(request): returns data to be returned by the view
    """

    def get(self, request, **kwargs):
        data = self.get_data(request, **kwargs)
        return HttpResponse(json.dumps(data),
                            content_type='application/json')


class ReportsJSON(BaseJSONDataView):
    @staticmethod
    def get_data(request):
        genome_analyses = GenomeAnalysis.objects.filter(user=request.user)
        return serializers.serialize("json", genome_analyses)


class GenomeReportJSONView(BaseJSONDataView):
    def get(self, request, **kwargs):
        print kwargs
        return super(GenomeReportJSONView, self).get(request, **kwargs)

    def get_data(self, request, **kwargs):
        genome_report = GenomeAnalysis.objects.get(pk=kwargs['pk'])
        return json.dumps(genome_report.shared_data_as_dict())
