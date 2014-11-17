"""Import external gene data."""

import gzip
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from ...models import Gene, RefSeqTranscriptID


def import_hgnc_data():
    """Add data from HGNC: Gene symbols, names, RefSeq transcripts."""
    hgnc_gene_data_filepath = os.path.join(
        settings.DATA_FILE_ROOT,
        'hgnc_gene_with_protein_product.txt.gz')
    hgnc_data = gzip.open(hgnc_gene_data_filepath)
    hgnc_data.next()
    genes = []
    refseq_correspondence = {}
    # Notes:
    #
    # This is using a bulk create - we check if a Gene exists and, if not,
    # create the object (without saving to db) and save in an array.
    # Then we use bulk_create to create everything.
    #
    # Because there may be multiple RefSeq IDs for a given gene, these are
    # stored in a RefSeqTranscriptID with many-to-one relationship to Gene.
    #
    # To create one of these objects, we need to have the relevant Gene
    # primary key - and because we're doing bulk creation, we don't have that.
    # So we store the gene symbols to look up corresponding Gene objects and
    # get the primary key later.
    #
    # You might ask: why don't we store the Gene objects themselves in that
    # dict, to skip later lookup? Using objects like this after "save" works
    # because Django's .save() updates an object with the relevant primary key,
    # but this doesn't happen when using "bulk_create".
    for line in hgnc_data:
        data = line.rstrip('\n').split('\t')
        hgnc_id, hgnc_symbol, hgnc_name = data[0:3]
        if Gene.objects.filter(hgnc_symbol=hgnc_symbol,
                               hgnc_id=hgnc_id,
                               hgnc_name=hgnc_name).exists():
            continue
        if Gene.objects.filter(hgnc_id=hgnc_id).exists():
            gene = Gene.objects.get(hgnc_id=hgnc_id)
            gene.hgnc_symbol = hgnc_symbol
            gene.hgnc_name = hgnc_name
        else:
            gene = Gene(hgnc_symbol=hgnc_symbol,
                        hgnc_id=hgnc_id,
                        hgnc_name=hgnc_name)
        genes.append(gene)
        refseq_ids = data[9].split(', ')
        for refseq_id in refseq_ids:
            if refseq_id:
                refseq_correspondence[refseq_id] = hgnc_symbol
    Gene.objects.bulk_create(genes)
    refseq_transcript_ids = []
    for refseq_id in refseq_correspondence.keys():
        gene = Gene.objects.get(hgnc_symbol=refseq_correspondence[refseq_id])
        refseq_transcript_id = RefSeqTranscriptID(
            refseq_id=refseq_id, gene=gene)
        refseq_transcript_ids.append(refseq_transcript_id)
    RefSeqTranscriptID.objects.bulk_create(refseq_transcript_ids)


class Command(BaseCommand):
    help = 'Adds external gene-related data to database'

    def handle(self, *args, **options):
        import_hgnc_data()
