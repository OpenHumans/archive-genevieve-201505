# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('variants', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='GenomeAnalysis',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField(verbose_name=b'File Name')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('uploadfile', models.FileField(upload_to=b'uploads/%Y/%m/%d')),
                ('processedfile', models.FileField(upload_to=b'processed/%Y/%m/%d', blank=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GenomeAnalysisVariant',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('zyg', models.TextField(verbose_name=b'Zygosity')),
                ('genomeanalysis', models.ForeignKey(to='genomes.GenomeAnalysis')),
                ('variant', models.ForeignKey(to='variants.Variant')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='genomeanalysis',
            name='variants',
            field=models.ManyToManyField(to='variants.Variant', through='genomes.GenomeAnalysisVariant'),
            preserve_default=True,
        ),
    ]
