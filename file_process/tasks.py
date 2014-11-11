"""Tasks for analyzing genome/genetic data files"""
# absolute_import prevents conflicts between project celery.py file
# and the celery package.
from __future__ import absolute_import
import csv
import gzip
import os
import re
from random import randint

from celery import shared_task

from django.conf import settings
from django.core.files import File

from .models import (Variant, ClinVarRecord, GenomeAnalysis,
                     GenomeAnalysisVariant)

from .utils import vcf_parsing_tools as vcftools
from .utils.conv23andMetoVCF import conv23andme_to_vcf
from .utils.twentythree_and_me import (api23andme_full_gen_data,
                                       api23andme_full_gen_infer_sex,
                                       api23andme_to_vcf)

CLINVAR_FILENAME = "clinvar-latest.vcf"


@shared_task
def analyze_23andme_from_api(access_token, profile_id, user):
    genome_data = api23andme_full_gen_data(access_token, profile_id)
    sex = api23andme_full_gen_infer_sex(genome_data)
    vcf_data = api23andme_to_vcf(genome_data, sex)
    targetdir = '/tmp'
    filename = '23andme-api-' + profile_id + '.vcf.gz'
    if os.path.exists(os.path.join(targetdir, filename)):
        inc = 2
        while os.path.exists(os.path.join(targetdir, filename)):
            filename = '23andme-api-' + profile_id + '-' + str(inc) + '.vcf.gz'
            inc += 1
    filepath = os.path.join(targetdir, filename)
    output_file = gzip.open(filepath, mode='wb')
    output_file.writelines(vcf_data)
    # Close to ensure it's *really* closed before using File.
    output_file.close()
    # Reopen as binary so we don't lose compression.
    vcf_file = open(filepath)
    django_file = File(vcf_file)
    new_analysis = GenomeAnalysis(uploadfile=django_file,
                                  user=user, name=filename)
    new_analysis.save()
    vcf_file.close()
    os.remove(filepath)
    read_input_genome(analysis_in=new_analysis)


@shared_task
def read_input_genome(analysis_in):
    """Read input genome, either 23andme or VCF, and match against ClinVar"""
    name = os.path.basename(analysis_in.uploadfile.path)
    hg19_2bit = os.path.join(settings.DATA_FILE_ROOT, 'hg19.2bit')
    if re.match(r"[-\w]+.vcf(_\w+)?.gz$", name):
        genome_file = gzip.GzipFile(mode='rb', compresslevel=9,
                                    fileobj=analysis_in.uploadfile)
        read_vcf(analysis_in, genome_file)
    elif re.match(r"[-\w]+.txt(_\w+)?.gz$", name):
        conv23Me_file = gzip.GzipFile(mode='rb', compresslevel=9,
                                      fileobj=analysis_in.uploadfile)
        genome_file = conv23andme_to_vcf(conv23Me_file, hg19_2bit)
        read_vcf(analysis_in, genome_file)
    else:
        print "Error with incorrect file name"


@shared_task
def read_vcf(analysis_in, genome_file):
    """Takes two .vcf files and returns matches"""
    clinvar_filepath = os.path.join(settings.DATA_FILE_ROOT, CLINVAR_FILENAME)
    clin_file = open(clinvar_filepath, 'r')

    # Creates a tmp file to write the .csv
    tmp_output_file_path = os.path.join(
        '/tmp', 'django_celery_fileprocess-' +
        str(randint(10000000, 99999999)) + '-' +
        os.path.basename(analysis_in.uploadfile.path))
    tmp_output_file = open(tmp_output_file_path, 'w')
    csv_out = csv.writer(tmp_output_file)
    header = ("Chromosome", "Position", "Name", "Significance", "Frequency",
              "Zygosity", "ACC URL")
    csv_out.writerow(header)

    matched_variants = vcftools.match_to_clinvar(genome_file, clin_file)

    for var in matched_variants:
        chrom = var[0]
        pos = var[1]
        ref_allele = var[2]
        alt_allele = var[3]
        name_acc = var[4]
        freq = var[5]
        zygosity = var[6]
        variant, created = Variant.objects.get_or_create(chrom=chrom,
                                                         pos=pos,
                                                         ref_allele=ref_allele,
                                                         alt_allele=alt_allele)
        if not variant.freq:
            variant.freq = freq
            variant.save()

        genomeanalysisvariant = GenomeAnalysisVariant.objects.create(
            genomeanalysis=analysis_in, variant=variant, zyg=zygosity)
        genomeanalysisvariant.save()
        for spec in name_acc:
            # for online report
            url = "http://www.ncbi.nlm.nih.gov/clinvar/" + str(spec[0])
            name = spec[1]
            clnsig = spec[2]

            record, created = ClinVarRecord.objects.get_or_create(
                accnum=spec[0], variant=variant, condition=name, clnsig=clnsig)
            record.save()
            # analysis_in.variants.add(variant)
            # for CSV output
            data = (chrom, pos, name, clnsig, freq, zygosity, url)
            csv_out.writerow(data)

    # closes the tmp file
    tmp_output_file.close()

    # opens the tmp file and creates an output processed file"
    csv_filename = os.path.basename(analysis_in.uploadfile.path) + '.csv'

    with open(tmp_output_file_path, 'rb') as file_out:
        output_file = File(file_out)
        analysis_in.processedfile.save(csv_filename, output_file)
