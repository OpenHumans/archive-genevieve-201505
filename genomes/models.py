from django.contrib.auth.models import User
from django.db import models

from variants.models import Variant


class GenomeAnalysis(models.Model):
    """Model for uploaded file and its processed output.

    Output is a processed output file
    """
    # This associates a user with a specific genome analysis.
    user = models.ForeignKey(User)
    name = models.TextField("File Name")
    timestamp = models.DateTimeField(auto_now_add=True)
    uploadfile = models.FileField(blank=True,
                                  upload_to='uploads/%Y/%m/%d')
    processedfile = models.FileField(blank=True,
                                     upload_to='processed/%Y/%m/%d')
    variants = models.ManyToManyField(Variant, through='GenomeAnalysisVariant')

    def __unicode__(self):
        return 'GenomeAnalysis for %s' % str(self.uploadfile)


class GenomeAnalysisVariant(models.Model):
    """Info specific to this genome-variant instance, e.g. zygosity"""
    genomeanalysis = models.ForeignKey(GenomeAnalysis)
    variant = models.ForeignKey(Variant)
    zyg = models.TextField("Zygosity")

    def __unicode__(self):
        return ('GenomeAnalysisVariant for %s %s' % (str(self.genomeanalysis),
                                                     str(self.variant)))
