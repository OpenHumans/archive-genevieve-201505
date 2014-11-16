# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ClinVarRecord',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('accnum', models.TextField(verbose_name=b'Accession Number')),
                ('condition', models.TextField(verbose_name=b'Condition Name')),
                ('clnsig', models.TextField(verbose_name=b'Clinvar Significance')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Variant',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('chrom', models.TextField(verbose_name=b'Chromosome')),
                ('pos', models.TextField(verbose_name=b'Position')),
                ('ref_allele', models.TextField(verbose_name=b'Reference Allele')),
                ('alt_allele', models.TextField(verbose_name=b'Alternate Allele')),
                ('freq', models.TextField(verbose_name=b'Allele Frequency')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='variant',
            unique_together=set([('chrom', 'pos', 'ref_allele', 'alt_allele')]),
        ),
        migrations.AddField(
            model_name='clinvarrecord',
            name='variant',
            field=models.ForeignKey(to='variants.Variant'),
            preserve_default=True,
        ),
    ]
