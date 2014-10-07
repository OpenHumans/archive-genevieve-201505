# -*- coding: utf-8 -*-
"""Views for genome reports and genetic variants"""
from django.http import Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth import logout

from .models import GenomeAnalysis, ClinVarRecord
from .forms import UploadForm
from .tasks import read_input_genome


def list_reports(request):
    """List all genome reports"""
    # Authenticate
    if not request.user.is_authenticated():
        return render_to_response('file_process/login_error.html')
    # Handle file upload
    if request.method == 'POST':
        print "in post"
        form = UploadForm(request.POST or None, request.FILES or None)
        user = request.user
        if form.is_valid():
            form.user = user
            new_analysis = GenomeAnalysis(
                uploadfile=request.FILES['uploadfile'],
                user=form.user, name=request.POST['reportname'])
            new_analysis.save()
            print "Sending to analysis"
            read_input_genome.delay(analysis_in=new_analysis)
            # Redirect to the uploaded files list after POST
            return HttpResponseRedirect(reverse('file_process.views.list_reports'))
    else:
        # A empty, unbound form
        form = UploadForm()

    # Load documents for the list page
    genome_analyses = GenomeAnalysis.objects.all()
    # Render list page with the documents and the form
    # Render list page with the documents and the form
    return render_to_response(
        'file_process/list_reports.html',
        {'genome_analyses': genome_analyses,
         'form': form,
         'username': request.user.username,
         'user': request.user,
         },
        context_instance=RequestContext(request)
    )


def report(request, genomeanalysis_id):
    """Details about a specific genome report"""
    # Authenticate
    if not request.user.is_authenticated():
        return render_to_response('file_process/login_error.html')
    try:
        specific_analysis = GenomeAnalysis.objects.get(pk=genomeanalysis_id)
    except GenomeAnalysis.DoesNotExist:
        raise Http404
    if request.user != specific_analysis.user:
        return render_to_response('file_process/not_authorized.html')
    else:
        return render_to_response(
            'file_process/report.html',
            {'genomeanalysis_id': genomeanalysis_id,
             'specific_analysis': specific_analysis}
            )


def logout_view(request):
    """Log out"""
    logout(request)


def commentary(request, variant_id):
    """Genevieve comments on a specific genetic variant"""
    # Authenticate
    if not request.user.is_authenticated():
        return render_to_response('file_process/login_error.html')
    try:
        specific_variant = ClinVarRecord.objects.get(pk=variant_id)
        return render_to_response(
            'file_process/community_comments.html',
            {'variant_id': variant_id,
             'specific_variant': specific_variant}
            )
    except ClinVarRecord.DoesNotExist:
        raise Http404
