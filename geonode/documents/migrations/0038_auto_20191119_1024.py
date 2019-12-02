# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0037_khnews'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='KHNews',
            new_name='KHNew',
        ),
    ]
