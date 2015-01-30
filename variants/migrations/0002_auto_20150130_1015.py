# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('variants', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clinvarrecord',
            name='accnum',
            field=models.CharField(max_length=16, verbose_name=b'Accession Number'),
        ),
        migrations.AlterField(
            model_name='clinvarrecord',
            name='clnsig',
            field=models.PositiveSmallIntegerField(verbose_name=b'ClinVar Clinical Significance', choices=[(0, b'Uncertain significance'), (1, b'Not provided'), (2, b'Benign'), (3, b'Likely benign'), (4, b'Likely pathogenic'), (5, b'Pathogenic'), (6, b'Drug response'), (7, b'Histocompatibility'), (255, b'Other')]),
        ),
        migrations.AlterField(
            model_name='variant',
            name='alt_allele',
            field=models.CharField(max_length=255, verbose_name=b'Alternate Allele'),
        ),
        migrations.AlterField(
            model_name='variant',
            name='chrom',
            field=models.CharField(max_length=2, verbose_name=b'Chromosome', choices=[(b'1', b'1'), (b'2', b'2'), (b'3', b'3'), (b'4', b'4'), (b'5', b'5'), (b'6', b'6'), (b'7', b'7'), (b'8', b'8'), (b'9', b'9'), (b'10', b'10'), (b'11', b'11'), (b'12', b'12'), (b'13', b'13'), (b'14', b'14'), (b'15', b'15'), (b'16', b'16'), (b'17', b'17'), (b'18', b'18'), (b'19', b'19'), (b'20', b'20'), (b'21', b'21'), (b'22', b'22'), (b'X', b'X'), (b'Y', b'Y'), (b'M', b'M')]),
        ),
        migrations.AlterField(
            model_name='variant',
            name='freq',
            field=models.DecimalField(null=True, verbose_name=b'Allele Frequency', max_digits=8, decimal_places=8, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(1.0)]),
        ),
        migrations.AlterField(
            model_name='variant',
            name='pos',
            field=models.PositiveIntegerField(verbose_name=b'Position'),
        ),
        migrations.AlterField(
            model_name='variant',
            name='ref_allele',
            field=models.CharField(max_length=255, verbose_name=b'Reference Allele'),
        ),
    ]
