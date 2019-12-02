# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0036_khdocument_khevent'),
    ]

    operations = [
        migrations.CreateModel(
            name='KHNews',
            fields=[
                ('document_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='documents.Document')),
            ],
            options={
                'abstract': False,
            },
            bases=('documents.document',),
        ),
    ]
