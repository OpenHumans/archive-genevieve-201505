import re

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import (CharField,
                              DecimalField,
                              ForeignKey,
                              Model,
                              TextField,
                              PositiveIntegerField,
                              PositiveSmallIntegerField)


CHROM_CHOICES = [(str(x), str(x)) for x in range(1, 23)+ ['X', 'Y', 'M']]


def chr_normalize(chr_str):
    chr_norm = chr_str
    if chr_norm in dict(CHROM_CHOICES):
        return chr_norm
    # Normalize to remove 'chr' prefixes
    re_chr_prefix = re.compile(r'^[Cc]hr(.{1,2})')
    if re_chr_prefix.search(chr_norm):
        chr_norm = re_chr_prefix.search(chr_norm).groups()[0]
    # Normalize other alternate labels
    chr_map = {'MT': 'M'}
    if chr_norm in chr_map:
        chr_norm = chr_map[chr_norm]
    if chr_norm in dict(CHROM_CHOICES):
        return chr_norm
    raise ValueError('Nonstandard chromosome value: ' + chr_str)


class Variant(Model):
    """
    Genetic variant information

    Model for a genetic variant, containing basic information unrelated to
    evaluations of its effect (e.g. on traits or diseases).
    """
    chrom = CharField("Chromosome", max_length=2, choices=CHROM_CHOICES)
    pos = PositiveIntegerField("Position")
    ref_allele = CharField("Reference Allele", max_length=255)
    alt_allele = CharField("Alternate Allele", max_length=255)
    freq = DecimalField("Allele Frequency", max_digits=9, decimal_places=8,
                        validators=[MinValueValidator(0.0),
                                    MaxValueValidator(1.0)],
                        null=True)

    class Meta:
        unique_together = ('chrom', 'pos', 'ref_allele', 'alt_allele')

    def __unicode__(self):
        return 'Var: %s %s %s' % (self.chrom, self.pos, self.alt_allele)


class ClinVarRecord(Model):
    """Stores info specific to the Clinvar Record about the variant"""
    CLNSIG_CHOICES = ((0, 'Uncertain significance'),
                      (1, 'Not provided'),
                      (2, 'Benign'),
                      (3, 'Likely benign'),
                      (4, 'Likely pathogenic'),
                      (5, 'Pathogenic'),
                      (6, 'Drug response'),
                      (7, 'Histocompatibility'),
                      (255, 'Other'))
    accnum = CharField("Accession Number", max_length=16)
    condition = TextField("Condition Name")
    clnsig = PositiveSmallIntegerField("ClinVar Clinical Significance",
                                 choices=CLNSIG_CHOICES)
    variant = ForeignKey(Variant)

    def __unicode__(self):
        return 'ClinVarRecord: %s' % self.accnum
