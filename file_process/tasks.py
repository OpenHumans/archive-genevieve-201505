# absolute_import prevents conflicts between project celery.py file
# and the celery package.
from __future__ import absolute_import
from datetime import datetime
import csv
import gzip
import os

from random import randint
from celery import shared_task
from .models import Variant

from django.conf import settings
from django.core.files import File

from .vcf_parsing_tools import (ClinVarEntry, ClinVarAllele, ClinVarData,
                                match_to_clinvar)

CLINVAR_FILENAME = "clinvar-latest.vcf" 


@shared_task
def timestamp():
    """An example celery task, appends datetime to a log file."""
    LOGFILE = os.path.join(settings.MEDIA_ROOT, 'stamped_log_file.txt')
    with open(LOGFILE, 'a') as logfile:
        datetime_str = str(datetime.now()) + '\n'
        logfile.write(datetime_str)

@shared_task
def read_vcf(analysis_in):
    CLINVAR_FILEPATH = os.path.join(settings.DATA_FILE_ROOT, CLINVAR_FILENAME)
    '''Takes two .vcf files and returns matches'''

    clin_file = open(CLINVAR_FILEPATH, 'r')
    genome_file = gzip.GzipFile(mode='rb', compresslevel=9,
                                fileobj=analysis_in.uploadfile)
    
    '''creates a tmp file to write the .csv'''
    tmp_output_file_path = os.path.join('/tmp', 'django_celery_fileprocess-' +
                                    str(randint(10000000,99999999)) + '-' +
                                    os.path.basename(analysis_in.uploadfile.path))
    tmp_output_file = open(tmp_output_file_path, 'w')
    a = csv.writer(tmp_output_file)
    header = ("Chromosome", "Position", "Zygosity", "ACC URL")
    a.writerow(header)

    matched_variants = match_to_clinvar(genome_file, clin_file)

    for var in matched_variants:
        chrom = var[0]
        pos = var[1]
        zygosity = var[2]
        acc = var[3]
        for m in acc:
            accstr = str(m)
            variant = Variant(accnum=accstr)
            variant.save()
            analysis_in.variants.add(variant)
            print "ACCNUM:"
            print variant
            print variant.accnum
            url = "http://www.ncbi.nlm.nih.gov/clinvar/" + \
                  accstr
            data = (chrom,
                    pos,
                    zygosity, url)
            datastr = str(data)
            var_report = Variant(report=datastr)
            var_report.save()
            analysis_in.variants.add(var_report)
            a.writerow(data)

    #closes the tmp file
    tmp_output_file.close()
    
    #opens the tmp file and creates an output processed file"
    csv_filename = os.path.basename(analysis_in.uploadfile.path) + '.csv'

    with open(tmp_output_file_path, 'rb') as f:
        output_file = File(f)    
        analysis_in.processedfile.save(csv_filename, output_file)
    
