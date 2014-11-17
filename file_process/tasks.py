"""Tasks for analyzing genome/genetic data files"""
# absolute_import prevents conflicts between project celery.py file
# and the celery package.
from __future__ import absolute_import
import bz2
import csv
import gzip
import os

from random import randint

from celery import shared_task

from django.conf import settings
from django.core.files import File

from genomes.models import GenomeAnalysis, GenomeAnalysisVariant
from variants.models import Variant, ClinVarRecord

from .utils import vcf_parsing_tools as vcftools
from .utils.twentythree_and_me import (api23andme_full_gen_data,
                                       api23andme_full_gen_infer_sex,
                                       api23andme_to_vcf)
from .utils.cgivar_to_vcf import convert as convert_cgivar_to_vcf

CLINVAR_FILENAME = "clinvar-latest-b37.vcf.gz"


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
    read_input_genome(analysis_in=new_analysis, genome_format='vcf')


@shared_task
def read_input_genome(analysis_in, genome_format='vcf'):
    """Read genome, VCF or Complete Genomics, and match against ClinVar"""
    name = os.path.basename(analysis_in.uploadfile.path)
    print genome_format
    if genome_format == 'cgivar':
        print "Treating as CGI var to be translated"
        genome_file = convert_cgivar_to_vcf(
            analysis_in.uploadfile.path,
            os.path.join(settings.DATA_FILE_ROOT, 'hg19.2bit'))
    elif name.endswith('.gz'):
        print "reading directly as gzip"
        genome_file = gzip.open(analysis_in.uploadfile.path, 'rb')
    elif name.endswith('.bz2'):
        print 'reading directly as bz2'
        genome_file = bz2.BZ2File(analysis_in.uploadfile.path, 'rb')
        # GzipFile(mode='rb', compresslevel=9,
        #                        fileobj=analysis_in.uploadfile)
    read_vcf(analysis_in, genome_file)


@shared_task
def read_vcf(analysis_in, genome_file):
    """Takes two .vcf files and returns matches"""
    clinvar_filepath = os.path.join(settings.DATA_FILE_ROOT, CLINVAR_FILENAME)
    clin_file = gzip.open(clinvar_filepath, 'r')

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
        print var
        chrom = var[0]
        pos = var[1]
        ref_allele = var[2]
        alt_allele = var[3]
        name_acc = var[4]
        freq = var[5]
        zygosity = var[6]
        variant, _ = Variant.objects.get_or_create(chrom=chrom,
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

            record, _ = ClinVarRecord.objects.get_or_create(
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
