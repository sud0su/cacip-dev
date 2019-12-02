# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('documents', '0034_auto_20191029_0531'),
    ]

    operations = [
        migrations.CreateModel(
            name='AuthorsTag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=100, verbose_name='Name')),
                ('slug', models.SlugField(unique=True, max_length=100, verbose_name='Slug')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AuthorsTaggedItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.IntegerField(verbose_name='Object id', db_index=True)),
                ('content_type', models.ForeignKey(related_name='documents_authorstaggeditem_tagged_items', verbose_name='Content type', to='contenttypes.ContentType')),
                ('tag', models.ForeignKey(to='documents.AuthorsTag')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='document',
            name='sourcetext',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='document',
            name='creators',
            field=taggit.managers.TaggableManager(to='documents.AuthorsTag', through='documents.AuthorsTaggedItem', blank=True, help_text=b'creators', verbose_name='creators'),
        ),
    ]
