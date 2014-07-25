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

import re
import csv
from .vcf_parsing_tools import (ClinVarEntry, ClinVarAllele, ClinVarData)

CLINVAR_FILENAME = "clinvar-latest.vcf" 

CHROM_INDEX = {"1": 1, "2": 2, "3": 3, "4": 4, "5": 5,
               "6": 6, "7": 7, "8": 8, "9": 9, "10": 10,
               "11": 11, "12": 12, "13": 13, "14": 14, "15": 15,
               "16": 16, "17": 17, "18": 18, "19": 19, "20": 20,
               "21": 21, "22": 22, "X": 23, "Y": 24, "M": 25,
           }
CLNSIG_INDEX = {0 : "unknown",
                1 : "untested",
                2 : "non-pathogenic",
                3 : "probably non-pathogenic",
                4 : "probably pathogenic",
                5 : "pathogenic",
                6 : "affecting drug response",
                7 : "affecting histocompatibility",
                255 : "other"
               }

@shared_task
def timestamp():
    """An example celery task, appends datetime to a log file."""
    LOGFILE = os.path.join(settings.MEDIA_ROOT, 'stamped_log_file.txt')
    with open(LOGFILE, 'a') as logfile:
        datetime_str = str(datetime.now()) + '\n'
        logfile.write(datetime_str)

def vcf_line_pos(vcf_line):
    """
    Very lightweight processing of vcf line to enable position matching.

    Returns a dict containing:
        'chrom': index of chromosome (int), indicates sort order
        'pos': position on chromosome (int)
    """
    if not vcf_line:
        return None
    vcf_data = vcf_line.strip().split("\t")
    return_data = dict()
    return_data['chrom'] = CHROM_INDEX[vcf_data[0]]
    return_data['pos'] = int(vcf_data[1])
    return return_data


def genome_vcf_line_alleles(vcf_line):
    if not vcf_line:
        return None
    vcf_data = vcf_line.strip().split("\t")
    possible_alleles = [vcf_data[3]] + vcf_data[4].split(',')
    format_tags = vcf_data[8].split(":")
    genome_values = vcf_data[9].split(":")
    genome_data = { format_tags[i]:genome_values[i] for i in
                    range(len(genome_values)) }
    alleles = [possible_alleles[int(x)] for x in
               re.split('[|/]', genome_data['GT'])
               if x != '.']
    return alleles

@shared_task
def read_vcf(file_in):
    CLINVAR_FILEPATH = os.path.join(settings.DATA_FILE_ROOT, CLINVAR_FILENAME)
    '''Takes two .vcf files and returns matches'''
    clin_file = open(CLINVAR_FILEPATH, 'r')

    genome_file = gzip.GzipFile(mode='rb', compresslevel=9,
                                fileobj=file_in.uploadfile)
    #genome_file = gzip.open(GENOME_FILEPATH, 'r')
    clin_curr_line = clin_file.next()
    genome_curr_line = genome_file.next()
    
    '''creates a tmp file to write the .csv'''
    tmp_output_file_path = os.path.join('/tmp', 'django_celery_fileprocess-' +
                                    str(randint(10000000,99999999)) + '-' +
                                    os.path.basename(file_in.uploadfile.path))
    tmp_output_file = open(tmp_output_file_path, 'w')
    a = csv.writer(tmp_output_file)
    header = ("Chromosome", "Position", "Zygosity", "ACC URL")
    a.writerow(header)
    
    # Ignores all the lines that start with a hashtag
    while clin_curr_line.startswith("#"):
        clin_curr_line = clin_file.next()
    while genome_curr_line.startswith("#"):
        genome_curr_line = genome_file.next()

    # Advance through both files simultaneously to find matches
    while clin_curr_line or genome_curr_line:

        clin_curr_pos = vcf_line_pos(clin_curr_line)
        genome_curr_pos = vcf_line_pos(genome_curr_line)
        if clin_curr_pos['chrom'] > genome_curr_pos['chrom']:
            # If the ClinVar chromosome is greater, advance the genome's file
            try:
                genome_curr_line = genome_file.next()
            except StopIteration:
                break

        elif clin_curr_pos['chrom'] < genome_curr_pos['chrom']:
            # If the genome's chromosome is greater, advance the ClinVar file
            try:
                clin_curr_line = clin_file.next()
            except StopIteration:
                break

        if clin_curr_pos['chrom'] == genome_curr_pos['chrom']:

            if clin_curr_pos['pos'] > genome_curr_pos['pos']:
                # If the ClinVar position is greater, advance the genome's file
                try:
                    genome_curr_line = genome_file.next()
                except StopIteration:
                    break
            elif clin_curr_pos['pos'] < genome_curr_pos['pos']:
                # If the genome's position is greater, advance the ClinVar file
                try:
                    clin_curr_line = clin_file.next()
                except StopIteration:
                    break
            # Start positions match, look for allele matching.
            else:
                # Figure out what alleles the genome has
                genome_alleles = genome_vcf_line_alleles(genome_curr_line)

                # Because ClinVar records can match ref allele, include
                # checks for both ref and alt alleles in both records.
                clinvar_data = ClinVarData(clin_curr_line)

                for genome_allele in genome_alleles:
                    # Using index so we can call up relevant ClinVarEntries
                    for i in range(len(clinvar_data.alleles)):
                        is_same_len_change = (
                            len(genome_allele) - len(genome_alleles[0]) ==
                             len(clinvar_data.alleles[i][0]) -
                             len(clinvar_data.alleles[0][0]))
                        is_match = (is_same_len_change and
                            (genome_allele.startswith(
                                clinvar_data.alleles[i][0])) or
                            (clinvar_data.alleles[i][0].startswith(
                                genome_allele)))
                        if is_match:
                            clinvar_data.alleles[i][1] += 1
                            
                for i in range(len(clinvar_data.alleles)):
                    zygosity = "???"
                    if (clinvar_data.alleles[i][1] and
                        clinvar_data.alleles[i][2]):
                        if len(genome_alleles) == 2:
                            if clinvar_data.alleles[i][1] == 1:
                                zygosity = "Het"
                            elif clinvar_data.alleles[i][1] == 2:
                                zygosity = "Hom"
                        elif len(genome_alleles) == 1:
                            if clinvar_data.alleles[i][1] == 1:
                                # Hemizygous, e.g. X chrom when XY.
                                zygosity = "Hem"
                                
                        clnsig = [int(clinvar_data.alleles[i][2].entries[x].sig) \
                                  for x in range(len(clinvar_data.alleles[i][2].entries))]
                        
                        acc = [clinvar_data.alleles[i][2].entries[n].acc \
                               for n in range(len(clnsig)) \
                               if clnsig[n] == 4 or clnsig[n] == 5]
                        if acc:
                            url_list = []
                            for m in acc:
                                file_in.accnum.save(str(m))
                                url = "http://www.ncbi.nlm.nih.gov/clinvar/" + \
                                        str(m)
                                data = (genome_curr_pos['chrom'],
                                        genome_curr_pos['pos'],
                                        zygosity, url)
                                a.writerow(data)
                                print data
                # Known bug: A couple ClinVar entries are swapped
                # relative to the genome: what the genome calls
                # reference, ClinVar calls alternate (and visa versa).
                # Currently these rare situations result in a non-match.
                try:
                    genome_curr_line = genome_file.next()
                    clin_curr_line = clin_file.next()
                except StopIteration:
                    break
    #closes the tmp file
    tmp_output_file.close()
    
    #opens the tmp file and creates an output processed file"
    csv_filename = os.path.basename(file_in.uploadfile.path) + '.csv'

    file_in.title.save(str(csv_filename))
    with open(tmp_output_file_path, 'rb') as f:
        output_file = File(f)    
        file_in.processedfile.save(csv_filename, output_file)
        
    #clean up
    os.remove(tmp_gzip_path)
