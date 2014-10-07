"""Models for genome reports and genetic variant information"""
from django.db import models
from django.contrib.auth.models import User


class Variant(models.Model):
    """Genetic variant basic information"""
    """Store info about a variant"""
    chrom = models.TextField("Chromosome")
    pos = models.TextField("Position")
    ref_allele = models.TextField("Reference Allele")
    alt_allele = models.TextField("Alternate Allele")
    freq = models.TextField("Allele Frequency")

    class Meta:
        unique_together = ('chrom', 'pos', 'ref_allele', 'alt_allele')

    def __unicode__(self):
        return 'Var: %s %s %s' % (self.chrom, self.pos, self.alt_allele)


class ClinVarRecord(models.Model):
    """Stores info specific to the Clinvar Record about the variant"""
    accnum = models.TextField("Accession Number")
    condition = models.TextField("Condition Name")
    clnsig = models.TextField("Clinvar Significance")
    variant = models.ForeignKey(Variant)

    def __unicode__(self):
        return 'ClinVarRecord: %s' % self.accnum


class GenomeAnalysis(models.Model):
    """Model for uploaded file and its processed output.

    Output is a processed output file
    """
    # This associates a user with a specific genome analysis.
    user = models.ForeignKey(User)
    name = models.TextField("File Name")
    timestamp = models.DateTimeField(auto_now_add=True)
    uploadfile = models.FileField(upload_to='uploads/%Y/%m/%d')
    processedfile = models.FileField(blank=True, upload_to='processed/%Y/%m/%d')
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
