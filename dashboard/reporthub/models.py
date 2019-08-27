from django.db import models
# from django.contrib.gis.db import models

class TempBeneficiaries(models.Model):
    index = models.BigIntegerField(blank=True, null=True)
    project_id = models.TextField(blank=True, null=True)
    report_id = models.TextField(blank=True, null=True)
    beneficiary_id = models.TextField(blank=True, null=True)
    cluster_id = models.TextField(blank=True, null=True)
    cluster = models.TextField(blank=True, null=True)
    focal_point_name = models.TextField(blank=True, null=True)
    focal_point_phone = models.TextField(blank=True, null=True)
    focal_point_email = models.TextField(blank=True, null=True)
    mpc_purpose_cluster_id = models.FloatField(blank=True, null=True)
    mpc_purpose_type_name = models.FloatField(blank=True, null=True)
    organization = models.TextField(blank=True, null=True)
    implementing_partners = models.TextField(blank=True, null=True)
    project_hrp_code = models.TextField(blank=True, null=True)
    project_code = models.TextField(blank=True, null=True)
    project_title = models.TextField(blank=True, null=True)
    project_start_date = models.TextField(blank=True, null=True)
    project_end_date = models.TextField(blank=True, null=True)
    donor = models.TextField(blank=True, null=True)
    report_month_number = models.BigIntegerField(blank=True, null=True)
    report_month = models.TextField(blank=True, null=True)
    report_year = models.BigIntegerField(blank=True, null=True)
    reporting_period = models.TextField(blank=True, null=True)
    admin0pcode = models.TextField(blank=True, null=True)
    admin0name = models.TextField(blank=True, null=True)
    admin1pcode = models.BigIntegerField(blank=True, null=True)
    admin1name = models.TextField(blank=True, null=True)
    admin2pcode = models.BigIntegerField(blank=True, null=True)
    admin2name = models.TextField(blank=True, null=True)
    admin3pcode = models.TextField(blank=True, null=True)
    admin3name = models.TextField(blank=True, null=True)
    admin4pcode = models.TextField(blank=True, null=True)
    admin4name = models.TextField(blank=True, null=True)
    admin5pcode = models.FloatField(blank=True, null=True)
    admin5name = models.FloatField(blank=True, null=True)
    conflict = models.NullBooleanField()
    site_id = models.TextField(blank=True, null=True)
    site_class = models.TextField(blank=True, null=True)
    site_status = models.TextField(blank=True, null=True)
    site_hub_id = models.FloatField(blank=True, null=True)
    site_hub_name = models.FloatField(blank=True, null=True)
    site_implementation_name = models.FloatField(blank=True, null=True)
    site_type_name = models.TextField(blank=True, null=True)
    site_name = models.TextField(blank=True, null=True)
    category_type_id = models.FloatField(blank=True, null=True)
    category_type_name = models.FloatField(blank=True, null=True)
    beneficiary_type_id = models.TextField(blank=True, null=True)
    beneficiary_type_name = models.TextField(blank=True, null=True)
    beneficiary_category_name = models.FloatField(blank=True, null=True)
    strategic_objective_id = models.TextField(blank=True, null=True)
    strategic_objective_name = models.TextField(blank=True, null=True)
    strategic_objective_description = models.TextField(blank=True, null=True)
    sector_objective_id = models.TextField(blank=True, null=True)
    sector_objective_name = models.TextField(blank=True, null=True)
    sector_objective_description = models.TextField(blank=True, null=True)
    activity_type_id = models.TextField(blank=True, null=True)
    activity_type_name = models.TextField(blank=True, null=True)
    activity_description_id = models.TextField(blank=True, null=True)
    activity_description_name = models.TextField(blank=True, null=True)
    activity_detail_id = models.TextField(blank=True, null=True)
    activity_detail_name = models.TextField(blank=True, null=True)
    indicator_id = models.TextField(blank=True, null=True)
    indicator_name = models.TextField(blank=True, null=True)
    activity_status_id = models.FloatField(blank=True, null=True)
    activity_status_name = models.FloatField(blank=True, null=True)
    delivery_type_id = models.TextField(blank=True, null=True)
    delivery_type_name = models.TextField(blank=True, null=True)
    distribution_status = models.TextField(blank=True, null=True)
    distribution_start_date = models.TextField(blank=True, null=True)
    distribution_end_date = models.TextField(blank=True, null=True)
    partial_kits = models.FloatField(blank=True, null=True)
    kit_details = models.FloatField(blank=True, null=True)
    units = models.BigIntegerField(blank=True, null=True)
    unit_type_id = models.TextField(blank=True, null=True)
    unit_type_name = models.TextField(blank=True, null=True)
    transfer_type_value = models.FloatField(blank=True, null=True)
    mpc_delivery_type_id = models.TextField(blank=True, null=True)
    mpc_delivery_type_name = models.TextField(blank=True, null=True)
    mpc_mechanism_type_id = models.FloatField(blank=True, null=True)
    mpc_mechanism_type_name = models.FloatField(blank=True, null=True)
    package_type_id = models.FloatField(blank=True, null=True)
    households = models.BigIntegerField(blank=True, null=True)
    families = models.BigIntegerField(blank=True, null=True)
    boys = models.BigIntegerField(blank=True, null=True)
    girls = models.BigIntegerField(blank=True, null=True)
    men = models.BigIntegerField(blank=True, null=True)
    women = models.BigIntegerField(blank=True, null=True)
    elderly_men = models.BigIntegerField(blank=True, null=True)
    elderly_women = models.BigIntegerField(blank=True, null=True)
    total = models.BigIntegerField(blank=True, null=True)
    admin1lng = models.FloatField(blank=True, null=True)
    admin1lat = models.FloatField(blank=True, null=True)
    admin2lng = models.FloatField(blank=True, null=True)
    admin2lat = models.FloatField(blank=True, null=True)
    admin3lng = models.FloatField(blank=True, null=True)
    admin3lat = models.FloatField(blank=True, null=True)
    admin4lng = models.FloatField(blank=True, null=True)
    admin4lat = models.FloatField(blank=True, null=True)
    admin5lng = models.FloatField(blank=True, null=True)
    admin5lat = models.FloatField(blank=True, null=True)
    site_lng = models.FloatField(blank=True, null=True)
    site_lat = models.FloatField(blank=True, null=True)
    updatedat = models.TextField(blank=True, null=True)
    createdat = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"temporary"."temp_beneficiaries"'