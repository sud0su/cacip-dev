# from django.db import models
from django.contrib.gis.db import models

class MegacampLandslideRisk(models.Model):
    gid = models.AutoField(primary_key=True)
    dn = models.IntegerField(blank=True, null=True)
    geom = models.MultiPolygonField(srid=32646, blank=True, null=True)
    geom_4326 = models.MultiPolygonField(blank=True, null=True)
    objects = models.GeoManager()

    class Meta:
        managed = False
        db_table = 'megacamp_landslide_risk'
