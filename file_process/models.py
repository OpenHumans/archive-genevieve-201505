from django.db import models

class GenomeAnalysis(models.Model):
    """Model for uploaded file and its processed output. Output is a processed output
    file"""
    uploadfile = models.FileField(upload_to='uploads/%Y/%m/%d')
    processedfile = models.FileField(blank=True, upload_to='processed/%Y/%m/%d')

class Variant(models.Model):
    accnum = models.CharField("accnum", max_length=30)

class Report(models.Model):
    """Model for the report.  One to one relationship with the genome file and many to
    many relationship with the variants"""
    title = models.CharField("file name", max_length=30)
    filereport = models.OneToOneField(GenomeAnalysis)
    variants = models.ManyToManyField(Variant)
