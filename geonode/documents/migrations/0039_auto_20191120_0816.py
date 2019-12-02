# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0038_auto_20191119_1024'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='KHNew',
            new_name='KHNews',
        ),
    ]
