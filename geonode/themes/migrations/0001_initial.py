# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='GeoNodeThemeCustomization',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text=b'This will not appear anywhere.', max_length=100)),
                ('date', models.DateTimeField(help_text=b'This will not appear anywhere.', auto_now_add=True)),
                ('description', models.TextField(help_text=b'This will not appear anywhere.', null=True, blank=True)),
                ('is_enabled', models.BooleanField(default=False, help_text=b'Enabling this theme will disable the current enabled theme (if any)')),
                ('logo', models.ImageField(null=True, upload_to=b'img/%Y/%m', blank=True)),
                ('jumbotron_bg', models.ImageField(upload_to=b'img/%Y/%m', null=True, verbose_name=b'Jumbotron background', blank=True)),
                ('jumbotron_welcome_hide', models.BooleanField(default=False, help_text=b'Check this if the jumbotron backgroud image already contains text', verbose_name=b'Hide text in the jumbotron')),
                ('jumbotron_welcome_title', models.CharField(max_length=255, null=True, verbose_name=b'Jumbotron title', blank=True)),
                ('jumbotron_welcome_content', models.TextField(null=True, verbose_name=b'Jumbotron content', blank=True)),
                ('jumbotron_cta_hide', models.BooleanField(default=False, verbose_name=b'Hide call to action')),
                ('jumbotron_cta_text', models.CharField(max_length=255, null=True, verbose_name=b'Call to action text', blank=True)),
                ('jumbotron_cta_link', models.CharField(max_length=255, null=True, verbose_name=b'Call to action link', blank=True)),
                ('body_color', models.CharField(default=b'#333333', max_length=10)),
                ('navbar_color', models.CharField(default=b'#333333', max_length=10)),
                ('jumbotron_color', models.CharField(default=b'#2c689c', max_length=10)),
                ('contactus', models.BooleanField(default=False, verbose_name=b'Enable contact us box')),
                ('contact_name', models.CharField(max_length=255, null=True, blank=True)),
                ('contact_position', models.CharField(max_length=255, null=True, blank=True)),
                ('contact_administrative_area', models.CharField(max_length=255, null=True, blank=True)),
                ('contact_street', models.CharField(max_length=255, null=True, blank=True)),
                ('contact_postal_code', models.CharField(max_length=255, null=True, blank=True)),
                ('contact_city', models.CharField(max_length=255, null=True, blank=True)),
                ('contact_country', models.CharField(max_length=255, null=True, blank=True)),
                ('contact_delivery_point', models.CharField(max_length=255, null=True, blank=True)),
                ('contact_voice', models.CharField(max_length=255, null=True, blank=True)),
                ('contact_facsimile', models.CharField(max_length=255, null=True, blank=True)),
                ('contact_email', models.CharField(max_length=255, null=True, blank=True)),
                ('partners_title', models.CharField(default=b'Our Partners', max_length=100, null=True, blank=True)),
                ('copyright', models.TextField(null=True, blank=True)),
                ('copyright_color', models.CharField(default=b'#2c689c', max_length=10)),
            ],
            options={
                'ordering': ('date',),
                'verbose_name_plural': 'Themes',
            },
        ),
        migrations.CreateModel(
            name='Partner',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('logo', models.ImageField(null=True, upload_to=b'img/%Y/%m', blank=True)),
                ('name', models.CharField(help_text=b'This will not appear anywhere.', max_length=100)),
                ('title', models.CharField(max_length=255, verbose_name=b'Display name')),
                ('href', models.CharField(max_length=255, verbose_name=b'Website')),
            ],
            options={
                'ordering': ('name',),
                'verbose_name_plural': 'Partners',
            },
        ),
        migrations.AddField(
            model_name='geonodethemecustomization',
            name='partners',
            field=models.ManyToManyField(related_name='partners', to='geonode_themes.Partner', blank=True),
        ),
    ]
