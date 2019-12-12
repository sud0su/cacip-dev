# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0027_auto_20190424_0915'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='areaofinterest',
            field=models.CharField(choices=[(b'watermanagement', 'Water Management'), (b'climatechange', 'Climate Change'), (b'riskassesment', 'Risk Assesment'), (b'foodsecurity', 'Food Security'), (b'sustainableagroecosystems', 'Sustainable Agroecosystems'), (b'landdegradation', 'Land Degradation')], max_length=100, blank=True, help_text='area of interest', null=True, verbose_name='Area of Interest'),
        ),
        migrations.AddField(
            model_name='profile',
            name='role',
            field=models.CharField(choices=[(b'citizen', 'Citizen'), (b'trainer', 'Trainer'), (b'researcher', 'Researcher'), (b'farmer', 'Farmer'), (b'decisionmaker', 'Decision Maker')], max_length=100, blank=True, help_text='role', null=True, verbose_name='Role'),
        ),
    ]
