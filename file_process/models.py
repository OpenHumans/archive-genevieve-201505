from django.db import models


class Variant(models.Model):
    """Store info about a variant"""
    accnum = models.CharField("accnum", max_length=30)
    report = models.TextField("report")

class GenomeAnalysis(models.Model):
    """Model for uploaded file and its processed output. Output is a processed output
    file"""
    uploadfile = models.FileField(upload_to='uploads/%Y/%m/%d')
    processedfile = models.FileField(blank=True, upload_to='processed/%Y/%m/%d')
    variants = models.ManyToManyField(Variant)
