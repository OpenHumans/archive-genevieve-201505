from django.contrib.auth.decorators import login_required
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.utils.decorators import method_decorator

from .models import GenomeAnalysis


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
