# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0039_auto_20191120_0816'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='KHEvent',
            new_name='Event',
        ),
        migrations.RenameModel(
            old_name='KHDocument',
            new_name='KnowledgehubDocument',
        ),
        migrations.RenameModel(
            old_name='KHNews',
            new_name='News',
        ),
        migrations.AddField(
            model_name='document',
            name='source_id',
            field=models.CharField(max_length=128, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='document',
            name='doc_type',
            field=models.CharField(default=b'Document', help_text='Document Type', max_length=128, verbose_name='Document Type', choices=[(b'MEET', b'Meetings Minute'), (b'ASSR', b'Assessment Report'), (b'Document', b'Document'), (b'MAPS', b'Map'), (b'FOCP', b'Focal Point List'), (b'SREP', b'Situation Report (SitRep)'), (b'PRES', b'Presentation'), (b'DASH', b'Dashboard'), (b'UPEV', b'Upcoming Event'), (b'RESP', b'Response Plan'), (b'Event', b'Event')]),
        ),
    ]
