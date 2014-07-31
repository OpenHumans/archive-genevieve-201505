from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

def home(request):
    return HttpResponse("Hello, Welcome to Genevieve.")
