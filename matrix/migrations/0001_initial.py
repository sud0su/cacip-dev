# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('base', '0034_auto_20190424_0915'),
    ]

    operations = [
        migrations.CreateModel(
            name='MatrixCertificate',
            fields=[
                ('email', models.CharField(max_length=200, serialize=False, primary_key=True)),
                ('first', models.CharField(max_length=200, blank=True)),
                ('last', models.CharField(max_length=200, blank=True)),
                ('percentage', models.FloatField(null=True, blank=True)),
                ('points_score', models.FloatField(null=True, blank=True)),
                ('points_available', models.FloatField(null=True, blank=True)),
                ('time_started', models.BigIntegerField(null=True, blank=True)),
                ('time_finished', models.BigIntegerField(null=True, blank=True)),
                ('cm_user_id', models.CharField(max_length=200, blank=True)),
            ],
            options={
                'db_table': 'matrix_certificate',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='matrix',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('action', models.CharField(help_text=b'for example "download,view"', max_length=255)),
                ('created', models.DateTimeField(editable=False)),
                ('resourceid', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, default=None, blank=True, to='base.ResourceBase', null=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
