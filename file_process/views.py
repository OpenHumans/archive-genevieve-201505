# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from .models import GenomeAnalysis
from .forms import UploadForm
from .tasks import timestamp, vcf_line_pos, genome_vcf_line_alleles, read_vcf

def list(request):
    # Handle file upload
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            new_analysis = GenomeAnalysis(uploadfile = request.FILES['uploadfile'])
            new_analysis.save()
            timestamp.delay()
            read_vcf.delay(analysis_in = new_analysis)
            # Redirect to the uploaded files list after POST
            return HttpResponseRedirect(reverse('file_process.views.list'))
    else:
        form = UploadForm() # A empty, unbound form

    # Load documents for the list page
    genome_analyses = GenomeAnalysis.objects.all()
    # Render list page with the documents and the form
    return render_to_response(
        'file_process/list.html',
        {'genome_analyses': genome_analyses,
         'form': form},
        context_instance=RequestContext(request)
    )

def report(request, genomeanalysis_id):
    try:
        specific_analysis = GenomeAnalysis.objects.get(pk=genomeanalysis_id)
    except GenomeAnalysis.DoesNotExist:
        raise Http404
    
    return render_to_response(
        'file_process/report.html',
        {'genomeanalysis_id': genomeanalysis_id,
         'specific_analysis': specific_analysis}
    )

