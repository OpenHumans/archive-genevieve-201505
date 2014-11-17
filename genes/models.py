from django.db import models


class Gene(models.Model):
    """Contains non-user-editable gene data.

    All of the following are required and required unique for all Genes.
    hgnc_symbol:    HGNC gene symbol (CharField)
    hgnc_name:      HGNC full name (CharField)
    hgnc_id:        HGNC gene ID (CharField)
    ncbi_gene_id:   NCBI gene ID (CharField)

    The remaining fields are potential additional data for genes.
    mim_id:           MIM (Mendelian Inheritance in Man) ID (CharField)
    clinical_testing: Listed in NCBI's Genetic Testing Registry (BooleanField)
    acmg_recommended: In ACMG's 2013 return of data guidelines (BooleanField)

    """

    hgnc_id = models.CharField(unique=True,
                               verbose_name='HGNC ID',
                               max_length=5,)
    hgnc_symbol = models.CharField(unique=True,
                                   null=True,
                                   verbose_name='HGNC gene symbol',
                                   max_length=15,)
    hgnc_name = models.TextField(verbose_name='HGNC gene name',
                                 null=True,
                                 )
    ncbi_gene_id = models.CharField(unique=True,
                                    null=True,
                                    verbose_name="NCBI Gene ID",
                                    max_length=9,)
    mim_id = models.CharField(null=True,
                              verbose_name="Mendelian Inheritance in Man ID",
                              max_length=6,)
    clinical_testing = models.BooleanField(default=False)
    acmg_recommended = models.BooleanField(default=False)

    def __unicode__(self):
        return self.hgnc_symbol

    @classmethod
    def gene_lookup(cls, gene_name):
        """Find and return Gene in database matching identifying string."""
        gene_match = cls.objects.get(hgnc_symbol__exact=gene_name)
        return gene_match


class RefSeqTranscriptID(models.Model):
    refseq_id = models.CharField(unique=True,
                                 verbose_name='Refseq ID',
                                 max_length=20)
    gene = models.ForeignKey(Gene)
