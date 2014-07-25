# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from .models import GenomeAnalysis
from .models import Report
from .forms import UploadForm
from .tasks import timestamp, vcf_line_pos, genome_vcf_line_alleles, read_vcf

def list(request):
    # Handle file upload
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            newfile = GenomeAnalysis(uploadfile = request.FILES['uploadfile'])
            newfile.save()
            timestamp.delay()
            read_vcf.delay(file_in = newfile)
            # Redirect to the uploaded files list after POST
            return HttpResponseRedirect(reverse('file_process.views.list'))
    else:
        form = UploadForm() # A empty, unbound form

    # Load documents for the list page
    uploadfiles = GenomeAnalysis.objects.all()
    reportform = Report.objects.all()
    # Render list page with the documents and the form
    return render_to_response(
        'file_process/list.html',
        {'uploadfiles': uploadfiles, 'reportform': reportform, 'form': form},
        context_instance=RequestContext(request)
    )
