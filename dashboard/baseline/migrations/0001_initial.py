# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BgdCampShelterfootprintUnosatReachV1Jan',
            fields=[
                ('fid', models.AutoField(serialize=False, primary_key=True)),
                ('the_geom', django.contrib.gis.db.models.fields.MultiPolygonField(srid=4326, null=True, blank=True)),
                ('id', models.CharField(max_length=80, null=True, blank=True)),
                ('un_class', models.CharField(max_length=80, null=True, blank=True)),
                ('area_m2', models.FloatField(null=True, blank=True)),
                ('area_class', models.CharField(max_length=80, null=True, blank=True)),
                ('dig_by', models.CharField(max_length=80, null=True, blank=True)),
                ('img_src', models.CharField(max_length=80, null=True, blank=True)),
                ('cmp_name', models.CharField(max_length=80, null=True, blank=True)),
            ],
            options={
                'db_table': 'BGD_Camp_ShelterFootprint_UNOSAT_REACH_v1_Jan',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='CampPop032019',
            fields=[
                ('fid', models.AutoField(serialize=False, primary_key=True)),
                ('the_geom', django.contrib.gis.db.models.fields.MultiPolygonField(srid=4326, null=True, blank=True)),
                ('objectid', models.BigIntegerField(null=True, db_column=b'OBJECTID', blank=True)),
                ('new_camp_n', models.CharField(max_length=254, null=True, db_column=b'New_Camp_N', blank=True)),
                ('district', models.CharField(max_length=254, null=True, db_column=b'District', blank=True)),
                ('upazila', models.CharField(max_length=254, null=True, db_column=b'Upazila', blank=True)),
                ('settlement', models.CharField(max_length=254, null=True, db_column=b'Settlement', blank=True)),
                ('union', models.CharField(max_length=50, null=True, db_column=b'Union', blank=True)),
                ('name_alias', models.CharField(max_length=50, null=True, db_column=b'Name_Alias', blank=True)),
                ('ssid', models.CharField(max_length=50, null=True, db_column=b'SSID', blank=True)),
                ('area_sqm', models.BigIntegerField(null=True, db_column=b'Area_SqM', blank=True)),
                ('area_acre', models.BigIntegerField(null=True, db_column=b'Area_Acre', blank=True)),
                ('shape_leng', models.FloatField(null=True, db_column=b'Shape_Leng', blank=True)),
                ('shape_area', models.FloatField(null=True, db_column=b'Shape_Area', blank=True)),
                ('id', models.IntegerField(null=True, db_column=b'ID', blank=True)),
                ('infant_fem', models.BigIntegerField(null=True, db_column=b'Infant_fem', blank=True)),
                ('infant_mal', models.BigIntegerField(null=True, db_column=b'Infant_mal', blank=True)),
                ('field_1_4_child', models.BigIntegerField(null=True, db_column=b'_1_4_Child', blank=True)),
                ('field_1_4_chil_field', models.BigIntegerField(null=True, db_column=b'_1_4_Chil_', blank=True)),
                ('field_5_11_chil', models.BigIntegerField(null=True, db_column=b'_5_11_Chil', blank=True)),
                ('field_5_11_chi_field', models.BigIntegerField(null=True, db_column=b'_5_11_Chi_', blank=True)),
                ('field_12_17_chi', models.BigIntegerField(null=True, db_column=b'_12_17_Chi', blank=True)),
                ('field_12_17_ch_field', models.BigIntegerField(null=True, db_column=b'_12_17_Ch_', blank=True)),
                ('field_18_59_adu', models.BigIntegerField(null=True, db_column=b'_18_59_Adu', blank=True)),
                ('field_18_59_ad_field', models.BigIntegerField(null=True, db_column=b'_18_59_Ad_', blank=True)),
                ('field_60_elderl', models.BigIntegerField(null=True, db_column=b'_60_Elderl', blank=True)),
                ('field_60_elde_1', models.BigIntegerField(null=True, db_column=b'_60_Elde_1', blank=True)),
                ('total_fami', models.BigIntegerField(null=True, db_column=b'Total_Fami', blank=True)),
                ('total_indi', models.BigIntegerField(null=True, db_column=b'Total_Indi', blank=True)),
                ('containhh', models.IntegerField(null=True, db_column=b'ContainHH', blank=True)),
                ('pcent_hh', models.IntegerField(null=True, db_column=b'Pcent_HH', blank=True)),
                ('pcent_hht', models.IntegerField(null=True, db_column=b'Pcent_HHT', blank=True)),
            ],
            options={
                'db_table': 'Camp_pop_03_2019',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='CxbHealthFacilities',
            fields=[
                ('fid', models.AutoField(serialize=False, primary_key=True)),
                ('the_geom', django.contrib.gis.db.models.fields.PointField(srid=4326, null=True, blank=True)),
                ('hf_uid', models.CharField(max_length=254, null=True, db_column=b'HF_UID', blank=True)),
                ('concantena', models.CharField(max_length=254, null=True, db_column=b'Concantena', blank=True)),
                ('facility_t', models.CharField(max_length=254, null=True, db_column=b'Facility_T', blank=True)),
                ('camp_name', models.CharField(max_length=254, null=True, db_column=b'Camp_Name', blank=True)),
                ('latitude', models.FloatField(null=True, db_column=b'Latitude', blank=True)),
                ('longitude', models.FloatField(null=True, db_column=b'Longitude', blank=True)),
                ('functional', models.CharField(max_length=254, null=True, db_column=b'Functional', blank=True)),
                ('field_24_7_faci', models.CharField(max_length=254, null=True, db_column=b'_24_7_faci', blank=True)),
                ('comment_on', models.CharField(max_length=254, null=True, db_column=b'Comment_on', blank=True)),
            ],
            options={
                'db_table': 'cxb_health_facilities',
                'managed': False,
            },
        ),
    ]
