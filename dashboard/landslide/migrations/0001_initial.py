# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MegacampLandslideRisk',
            fields=[
                ('gid', models.AutoField(serialize=False, primary_key=True)),
                ('dn', models.IntegerField(null=True, blank=True)),
                ('geom', django.contrib.gis.db.models.fields.MultiPolygonField(srid=32646, null=True, blank=True)),
                ('geom_4326', django.contrib.gis.db.models.fields.MultiPolygonField(srid=4326, null=True, blank=True)),
            ],
            options={
                'db_table': 'megacamp_landslide_risk',
                'managed': False,
            },
        ),
    ]
