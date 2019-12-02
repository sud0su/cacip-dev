# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('geonode_client', '0004_auto_20180416_1319'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='geonodethemecustomization',
            name='partners',
        ),
        migrations.DeleteModel(
            name='GeoNodeThemeCustomization',
        ),
        migrations.DeleteModel(
            name='Partner',
        ),
    ]
