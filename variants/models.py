from django.db import models


class Variant(models.Model):
    """Genetic variant basic information"""
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
