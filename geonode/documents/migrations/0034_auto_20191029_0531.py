# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0033_auto_20190507_0902'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='doc_type',
            field=models.CharField(default=b'MAPS', help_text='Document Type', max_length=128, verbose_name='Document Type', choices=[(b'MEET', b'Meetings Minute'), (b'ASSR', b'Assessment Report'), (b'MAPS', b'Map'), (b'FOCP', b'Focal Point List'), (b'SREP', b'Situation Report (SitRep)'), (b'PRES', b'Presentation'), (b'DASH', b'Dashboard'), (b'UPEV', b'Upcoming Event'), (b'RESP', b'Response Plan')]),
        ),
    ]
