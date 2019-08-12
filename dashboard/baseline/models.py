# from django.db import models
from django.contrib.gis.db import models

class CampPop032019(models.Model):
    fid = models.AutoField(primary_key=True)
    the_geom = models.MultiPolygonField(blank=True, null=True)
    objectid = models.BigIntegerField(db_column='OBJECTID', blank=True, null=True)  # Field name made lowercase.
    new_camp_n = models.CharField(db_column='New_Camp_N', max_length=254, blank=True, null=True)  # Field name made lowercase.
    district = models.CharField(db_column='District', max_length=254, blank=True, null=True)  # Field name made lowercase.
    upazila = models.CharField(db_column='Upazila', max_length=254, blank=True, null=True)  # Field name made lowercase.
    settlement = models.CharField(db_column='Settlement', max_length=254, blank=True, null=True)  # Field name made lowercase.
    union = models.CharField(db_column='Union', max_length=50, blank=True, null=True)  # Field name made lowercase.
    name_alias = models.CharField(db_column='Name_Alias', max_length=50, blank=True, null=True)  # Field name made lowercase.
    ssid = models.CharField(db_column='SSID', max_length=50, blank=True, null=True)  # Field name made lowercase.
    area_sqm = models.BigIntegerField(db_column='Area_SqM', blank=True, null=True)  # Field name made lowercase.
    area_acre = models.BigIntegerField(db_column='Area_Acre', blank=True, null=True)  # Field name made lowercase.
    shape_leng = models.FloatField(db_column='Shape_Leng', blank=True, null=True)  # Field name made lowercase.
    shape_area = models.FloatField(db_column='Shape_Area', blank=True, null=True)  # Field name made lowercase.
    id = models.IntegerField(db_column='ID', blank=True, null=True)  # Field name made lowercase.
    infant_fem = models.BigIntegerField(db_column='Infant_fem', blank=True, null=True)  # Field name made lowercase.
    infant_mal = models.BigIntegerField(db_column='Infant_mal', blank=True, null=True)  # Field name made lowercase.
    field_1_4_child = models.BigIntegerField(db_column='_1_4_Child', blank=True, null=True)  # Field name made lowercase. Field renamed because it started with '_'.
    field_1_4_chil_field = models.BigIntegerField(db_column='_1_4_Chil_', blank=True, null=True)  # Field name made lowercase. Field renamed because it started with '_'. Field renamed because it ended with '_'.
    field_5_11_chil = models.BigIntegerField(db_column='_5_11_Chil', blank=True, null=True)  # Field name made lowercase. Field renamed because it started with '_'.
    field_5_11_chi_field = models.BigIntegerField(db_column='_5_11_Chi_', blank=True, null=True)  # Field name made lowercase. Field renamed because it started with '_'. Field renamed because it ended with '_'.
    field_12_17_chi = models.BigIntegerField(db_column='_12_17_Chi', blank=True, null=True)  # Field name made lowercase. Field renamed because it started with '_'.
    field_12_17_ch_field = models.BigIntegerField(db_column='_12_17_Ch_', blank=True, null=True)  # Field name made lowercase. Field renamed because it started with '_'. Field renamed because it ended with '_'.
    field_18_59_adu = models.BigIntegerField(db_column='_18_59_Adu', blank=True, null=True)  # Field name made lowercase. Field renamed because it started with '_'.
    field_18_59_ad_field = models.BigIntegerField(db_column='_18_59_Ad_', blank=True, null=True)  # Field name made lowercase. Field renamed because it started with '_'. Field renamed because it ended with '_'.
    field_60_elderl = models.BigIntegerField(db_column='_60_Elderl', blank=True, null=True)  # Field name made lowercase. Field renamed because it started with '_'.
    field_60_elde_1 = models.BigIntegerField(db_column='_60_Elde_1', blank=True, null=True)  # Field name made lowercase. Field renamed because it started with '_'.
    total_fami = models.BigIntegerField(db_column='Total_Fami', blank=True, null=True)  # Field name made lowercase.
    total_indi = models.BigIntegerField(db_column='Total_Indi', blank=True, null=True)  # Field name made lowercase.
    containhh = models.IntegerField(db_column='ContainHH', blank=True, null=True)  # Field name made lowercase.
    pcent_hh = models.IntegerField(db_column='Pcent_HH', blank=True, null=True)  # Field name made lowercase.
    pcent_hht = models.IntegerField(db_column='Pcent_HHT', blank=True, null=True)  # Field name made lowercase.
    objects = models.GeoManager()

    class Meta:
        managed = False
        db_table = 'Camp_pop_03_2019'

class BgdCampShelterfootprintUnosatReachV1Jan(models.Model):
    fid = models.AutoField(primary_key=True)
    the_geom = models.MultiPolygonField(blank=True, null=True)
    id = models.CharField(max_length=80, blank=True, null=True)
    un_class = models.CharField(max_length=80, blank=True, null=True)
    area_m2 = models.FloatField(blank=True, null=True)
    area_class = models.CharField(max_length=80, blank=True, null=True)
    dig_by = models.CharField(max_length=80, blank=True, null=True)
    img_src = models.CharField(max_length=80, blank=True, null=True)
    cmp_name = models.CharField(max_length=80, blank=True, null=True)
    objects = models.GeoManager()

    class Meta:
        managed = False
        db_table = 'BGD_Camp_ShelterFootprint_UNOSAT_REACH_v1_Jan'

class CxbHealthFacilities(models.Model):
    fid = models.AutoField(primary_key=True)
    the_geom = models.PointField(blank=True, null=True)
    hf_uid = models.CharField(db_column='HF_UID', max_length=254, blank=True, null=True)  # Field name made lowercase.
    concantena = models.CharField(db_column='Concantena', max_length=254, blank=True, null=True)  # Field name made lowercase.
    facility_t = models.CharField(db_column='Facility_T', max_length=254, blank=True, null=True)  # Field name made lowercase.
    camp_name = models.CharField(db_column='Camp_Name', max_length=254, blank=True, null=True)  # Field name made lowercase.
    latitude = models.FloatField(db_column='Latitude', blank=True, null=True)  # Field name made lowercase.
    longitude = models.FloatField(db_column='Longitude', blank=True, null=True)  # Field name made lowercase.
    functional = models.CharField(db_column='Functional', max_length=254, blank=True, null=True)  # Field name made lowercase.
    field_24_7_faci = models.CharField(db_column='_24_7_faci', max_length=254, blank=True, null=True)  # Field renamed because it started with '_'.
    comment_on = models.CharField(db_column='Comment_on', max_length=254, blank=True, null=True)  # Field name made lowercase.
    objects = models.GeoManager()

    class Meta:
        managed = False
        db_table = 'cxb_health_facilities'

