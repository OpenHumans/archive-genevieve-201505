from django.contrib.auth.decorators import login_required
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.utils.decorators import method_decorator

from .models import GenomeAnalysis
from file_process.views import make_auth_23andme_url


class GenomeAnalysesView(ListView):

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(GenomeAnalysesView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        genome_analyses = GenomeAnalysis.objects.filter(user=self.request.user)
        return genome_analyses

    def get_context_data(self, **kwargs):
        context = super(GenomeAnalysesView, self).get_context_data(**kwargs)
        additional_context = {
            'auth_23andme_url': make_auth_23andme_url(),
        }
        context.update(additional_context)
        return context


class GenomeReportView(DetailView):
    model = GenomeAnalysis

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(GenomeReportView, self).dispatch(*args, **kwargs)
