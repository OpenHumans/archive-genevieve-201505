# -*- coding: utf-8 -*-
"""Views for genome reports and genetic variants"""

import requests

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.views.generic.edit import FormView
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.decorators import method_decorator

from genomes.models import GenomeAnalysis
from variants.models import ClinVarRecord

from .forms import GenomeUploadForm
from .tasks import read_input_genome, analyze_23andme_from_api


def make_auth_23andme_url():
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
        'redirect_uri': settings.REDIRECT_URI,
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
    return None, None


def receive_23andme(request):
    """Receive 23andme authorization, prompt selection of account data."""
    data, access_token = complete_23andme_auth(request.GET['code'])
    if data and access_token:
        request.session['23andme_access_token'] = access_token
        return render_to_response('file_process/select_23andme.html',
                                  {'profiles': data['profiles']},
                                  context_instance=RequestContext(request))
    else:
        return HttpResponse("Sorry, unable to retrieve token!")


def complete_23andme(request):
    """Initiate 23andme import and processing and redirect to reports list"""
    if request.method == 'POST':
        if 'profile_id' in request.POST:
            print "Sending to analyze_23andme_from_api"
            analyze_23andme_from_api.delay(
                request.session['23andme_access_token'],
                request.POST['profile_id'], request.user)
            return HttpResponseRedirect(
                reverse('genomes:reports_list'))
        else:
            return HttpResponse("Sorry that didn't seem to work")


class GenomeImportView(FormView):
    form_class = GenomeUploadForm
    success_url = '/genomes/'
    template_name = 'file_process/genome_import.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(GenomeImportView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        form.user = self.request.user
        new_analysis = GenomeAnalysis(
            uploadfile=self.request.FILES['uploadfile'],
            user=form.user, name=self.request.POST['reportname'])
        genome_format = self.request.POST['genome_format']
        new_analysis.save()
        read_input_genome.delay(analysis_in=new_analysis,
                                genome_format=genome_format)
        return super(GenomeImportView, self).form_valid(form)

    def get_context_data(self, **kwargs):
            context = super(GenomeImportView, self).get_context_data(**kwargs)
            additional_context = {
                'auth_23andme_url': make_auth_23andme_url(),
            }
            context.update(additional_context)
            return context


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
