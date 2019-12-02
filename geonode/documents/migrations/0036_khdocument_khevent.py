# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0035_auto_20191108_0348'),
    ]

    operations = [
        migrations.CreateModel(
            name='KHDocument',
            fields=[
                ('document_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='documents.Document')),
            ],
            options={
                'abstract': False,
            },
            bases=('documents.document',),
        ),
        migrations.CreateModel(
            name='KHEvent',
            fields=[
                ('document_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='documents.Document')),
                ('event_date_start', models.DateTimeField(default=django.utils.timezone.now, help_text=b'Event date start', verbose_name='Event date start')),
                ('event_date_end', models.DateTimeField(default=django.utils.timezone.now, help_text=b'Event date end', verbose_name='Event date end')),
            ],
            options={
                'abstract': False,
            },
            bases=('documents.document',),
        ),
    ]
