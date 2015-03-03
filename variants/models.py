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

    def shared_data_as_dict(self):
        return {
            'id': self.id,
            'chrom': self.chrom,
            'pos': self.pos,
            'ref_allele': self.ref_allele,
            'alt_allele': self.alt_allele,
            'freq': self.freq,
            'clinvarrecords_dataset':
                {r.id: r.shared_data_as_dict() for r in self.clinvarrecord_set.all()},
            }


class ClinVarRecord(models.Model):
    """Stores info specific to the Clinvar Record about the variant"""
    accnum = models.TextField("Accession Number")
    condition = models.TextField("Condition Name")
    clnsig = models.TextField("Clinvar Significance")
    variant = models.ForeignKey(Variant)

    def shared_data_as_dict(self):
        return {
            'id': self.id,
            'accnum': self.accnum,
            'condition': self.condition,
            'clnsig': self.clnsig,
            'variant_id': self.variant.id,
        }

    def __unicode__(self):
        return 'ClinVarRecord: %s' % self.accnum
