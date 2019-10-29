# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0032_auto_20180412_0822'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='datasource',
            field=models.CharField(max_length=128, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='document',
            name='papersize',
            field=models.CharField(max_length=2, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='document',
            name='subtitle',
            field=models.CharField(max_length=128, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='document',
            name='version',
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
    ]
