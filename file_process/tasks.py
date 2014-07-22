from __future__ import absolute_import
from datetime import datetime
import gzip
import os
import re

from random import randint
from celery import shared_task
from django.conf import settings
from django.core.files import File
from django.core.files.base import ContentFile

@shared_task
def timestamp():
    LOGFILE = os.path.join(settings.MEDIA_ROOT, 'stamped_log_file.txt')
    with open(LOGFILE, 'a') as logfile:
        datetime_str = str(datetime.now()) + '\n'
        logfile.write(datetime_str)

@shared_task
def gzip_compress(file_in):
    input_file = file_in.uploadfile
    # output_file = file_in.processedfile
    print input_file
    print input_file.url
    print input_file.path
    output_file_path = re.sub('/media/uploads', '/media/processed', input_file.url) + '.gzip'
    for line in input_file:
        print line

    output_file = None
    gzip_filename = os.path.basename(input_file.path) + '.gz'
    tmp_gzip_path = os.path.join('/tmp', 'django_celery_fileprocess-' + str(randint(100000,999999)) + '-' + gzip_filename)
    with gzip.open(tmp_gzip_path, 'wb+') as gzip_out:
        gzip_out.writelines(input_file)
        gzip_out.close()

    with open(tmp_gzip_path, 'rb') as f:
        output_file = File(f)    
        file_in.processedfile.save(gzip_filename, output_file)
