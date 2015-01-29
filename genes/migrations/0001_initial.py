# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Gene',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('hgnc_id', models.CharField(unique=True, max_length=5, verbose_name=b'HGNC ID')),
                ('hgnc_symbol', models.CharField(max_length=15, unique=True, null=True, verbose_name=b'HGNC gene symbol')),
                ('hgnc_name', models.TextField(null=True, verbose_name=b'HGNC gene name')),
                ('ncbi_gene_id', models.CharField(max_length=9, unique=True, null=True, verbose_name=b'NCBI Gene ID')),
                ('mim_id', models.CharField(max_length=6, null=True, verbose_name=b'Mendelian Inheritance in Man ID')),
                ('clinical_testing', models.BooleanField(default=False)),
                ('acmg_recommended', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RefSeqTranscriptID',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('refseq_id', models.CharField(unique=True, max_length=20, verbose_name=b'Refseq ID')),
                ('gene', models.ForeignKey(to='genes.Gene')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
