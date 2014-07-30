from django.db import models

class Variant(models.Model):
    """Store info about a variant"""
    chrom = models.TextField("Chromosome")
    pos = models.TextField("Position")
    ref_allele = models.TextField("Reference allele")
    alt_allele = models.TextField("Alternate allele")
    zyg = models.TextField("Zygosity")

class ClinVarRecord(models.Model):
    accnum = models.TextField("Accession Number")
    condition = models.TextField("Condition Name")
    variant = models.ForeignKey(Variant)

class GenomeAnalysis(models.Model):
    """Model for uploaded file and its processed output. Output is a processed output
    file"""
    uploadfile = models.FileField(upload_to='uploads/%Y/%m/%d')
    processedfile = models.FileField(blank=True, upload_to='processed/%Y/%m/%d')
    variants = models.ManyToManyField(Variant)
