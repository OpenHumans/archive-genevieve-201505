# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('genomes', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='genomeanalysis',
            name='uploadfile',
            field=models.FileField(upload_to=b'uploads/%Y/%m/%d', blank=True),
        ),
    ]
