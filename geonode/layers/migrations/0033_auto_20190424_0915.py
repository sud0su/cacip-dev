# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('layers', '0032_auto_20180424_1638'),
    ]

    operations = [
        migrations.AlterField(
            model_name='layer',
            name='elevation_regex',
            field=models.CharField(max_length=128, null=True, verbose_name='Elevation regex', blank=True),
        ),
        migrations.AlterField(
            model_name='layer',
            name='has_elevation',
            field=models.BooleanField(default=False, verbose_name='Has elevation?'),
        ),
        migrations.AlterField(
            model_name='layer',
            name='has_time',
            field=models.BooleanField(default=False, verbose_name='Has time?'),
        ),
        migrations.AlterField(
            model_name='layer',
            name='is_mosaic',
            field=models.BooleanField(default=False, verbose_name='Is mosaic?'),
        ),
        migrations.AlterField(
            model_name='layer',
            name='name',
            field=models.CharField(max_length=128, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='layer',
            name='store',
            field=models.CharField(max_length=128, verbose_name='Store'),
        ),
        migrations.AlterField(
            model_name='layer',
            name='storeType',
            field=models.CharField(max_length=128, verbose_name='Storetype'),
        ),
        migrations.AlterField(
            model_name='layer',
            name='time_regex',
            field=models.CharField(blank=True, max_length=128, null=True, verbose_name='Time regex', choices=[(b'[0-9]{8}', 'YYYYMMDD'), (b'[0-9]{8}T[0-9]{6}', "YYYYMMDD'T'hhmmss"), (b'[0-9]{8}T[0-9]{6}Z', "YYYYMMDD'T'hhmmss'Z'")]),
        ),
        migrations.AlterField(
            model_name='layer',
            name='typename',
            field=models.CharField(max_length=128, null=True, verbose_name='Typename', blank=True),
        ),
        migrations.AlterField(
            model_name='layer',
            name='workspace',
            field=models.CharField(max_length=128, verbose_name='Workspace'),
        ),
    ]
