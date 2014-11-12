# -*- coding: utf-8 -*-
"""Views for genome reports and genetic variants"""
import json

import requests

from django.http import Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import logout
from django.conf import settings
from django.core.urlresolvers import reverse

from .models import GenomeAnalysis, ClinVarRecord
from .forms import UploadForm
from .tasks import read_input_genome, analyze_23andme_from_api


def make_auth_23andme_url(url_type=None):
    return ("https://api.23andme.com/authorize/?" +
            "&".join(["response_type=code",
                      "client_id=%s" % settings.CLIENT_ID_23ANDME,
                      "scope=%s" % "basic names genomes"]))


def complete_23andme_auth(code):
    parameters = {
        'client_id': settings.CLIENT_ID_23ANDME,
        'client_secret': settings.CLIENT_SECRET_23ANDME,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': 'http://localhost:8000/file_process/receive_23andme/',
        'scope': 'basic names genomes'
    }
    token_req = requests.post("https://api.23andme.com/token/",
                              data=parameters, verify=False)
    if token_req.status_code == 200 and 'access_token' in token_req.json():
        access_token = token_req.json()['access_token']
        headers = {'Authorization': 'Bearer %s' % access_token}
        names_req = requests.get("https://api.23andme.com/1/names/",
                                 headers=headers, verify=False)
        if names_req.status_code == 200:
            return names_req.json(), access_token
    return None


def list_reports(request):
    """List all genome reports"""
    # Authenticate
    if not request.user.is_authenticated():
        return render_to_response('file_process/login_error.html')
    # Handle file upload
    if request.method == 'POST':
        print "list_reports: in POST"
        form = UploadForm(request.POST or None, request.FILES or None)
        user = request.user
        if form.is_valid():
            form.user = user
            new_analysis = GenomeAnalysis(
                uploadfile=request.FILES['uploadfile'],
                user=form.user, name=request.POST['reportname'])
            genome_format = request.POST['genome_format']
            new_analysis.save()
            print "Sending to analysis with format " + genome_format
            read_input_genome.delay(analysis_in=new_analysis,
                                    genome_format=genome_format)
            # Redirect to the uploaded files list after POST
            return HttpResponseRedirect(reverse('file_process.views.list_reports'))
    else:
        # A empty, unbound form
        form = UploadForm()

    # Load documents for the list page
    genome_analyses = GenomeAnalysis.objects.all()
    # Render list page with the documents and the form
    return render_to_response(
        'file_process/list_reports.html',
        {'genome_analyses': genome_analyses,
         'form': form,
         'username': request.user.username,
         'user': request.user,
         'auth_23andme_url': make_auth_23andme_url(),
         },
        context_instance=RequestContext(request)
    )


def receive_23andme(request):
    """Receive 23andme authorization, prompt selection of account data."""
    data, access_token = complete_23andme_auth(request.GET['code'])
    request.session['23andme_access_token'] = access_token
    if data:
        return render_to_response('file_process/select_23andme.html',
                                  {'profiles': data['profiles']},
                                  context_instance=RequestContext(request))
    else:
        return HttpResponse("Sorry, unable to retrieve token!")


def complete_23andme(request):
    """Initiate 23andme import and processing and redirect to reports list"""
    print request
    if request.method == 'POST':
        if 'profile_id' in request.POST:
            print "Sending to analyze_23andme_from_api"
            analyze_23andme_from_api.delay(request.session['23andme_access_token'],
                                           request.POST['profile_id'], request.user)
            return HttpResponseRedirect(reverse('file_process.views.list_reports'))
        else:
            return HttpResponse("Sorry that didn't seem to work")


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
