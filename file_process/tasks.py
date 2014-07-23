# absolute_import prevents conflicts between project celery.py file
# and the celery package.
from __future__ import absolute_import
from datetime import datetime
import gzip
import os

from random import randint
from celery import shared_task

from django.conf import settings
from django.core.files import File

@shared_task
def timestamp():
    """An example celery task, appends datetime to a log file."""
    LOGFILE = os.path.join(settings.MEDIA_ROOT, 'stamped_log_file.txt')
    with open(LOGFILE, 'a') as logfile:
        datetime_str = str(datetime.now()) + '\n'
        logfile.write(datetime_str)

@shared_task
def gzip_compress(file_in):
    """
    Example celery asynchronous file processing task, performs gzip.

    arguments:
    file_in: an UploadFile model instance
    """
    input_file = file_in.uploadfile
    gzip_filename = os.path.basename(input_file.path) + '.gz'
    tmp_gzip_path = os.path.join('/tmp', 'django_celery_fileprocess-' +
                                 str(randint(10000000,99999999)) + '-' +
                                 gzip_filename)

    # Create temporary output file, compressed with gzip.
    with gzip.open(tmp_gzip_path, 'wb+') as gzip_out:
        gzip_out.writelines(input_file)
        gzip_out.close()

    # After closing, reopen the temporary output file as Django File object
    # and use that to save the file as the processedfile FileField.
    with open(tmp_gzip_path, 'rb') as f:
        output_file = File(f)    
        file_in.processedfile.save(gzip_filename, output_file)

    # Clean up.
    os.remove(tmp_gzip_path)

