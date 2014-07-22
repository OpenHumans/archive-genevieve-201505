# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from .models import UploadFile
from .forms import UploadForm
from .tasks import timestamp, gzip_compress

def list(request):
    # Handle file upload
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            newfile = UploadFile(uploadfile = request.FILES['uploadfile'])
            newfile.save()
            timestamp.delay()
            gzip_compress.delay(file_in = newfile)
            # Redirect to the uploaded files list after POST
            return HttpResponseRedirect(reverse('file_process.views.list'))
    else:
        form = UploadForm() # A empty, unbound form

    # Load documents for the list page
    uploadfiles = UploadFile.objects.all()

    # Render list page with the documents and the form
    return render_to_response(
        'file_process/list.html',
        {'uploadfiles': uploadfiles, 'form': form},
        context_instance=RequestContext(request)
    )
