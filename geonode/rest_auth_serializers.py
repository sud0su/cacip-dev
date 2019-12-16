from rest_framework import serializers
from rest_auth.registration.serializers import RegisterSerializer
from geonode.people.enumerations import AREA_OF_INTERESTS, CACIP_USER_ROLE_VALUES
from geonode.base.enumerations import COUNTRIES
from allauth.account.adapter import get_adapter

class CustomRegisterSerializer(RegisterSerializer):
    country = serializers.ChoiceField(
        choices=COUNTRIES
    )
    areaofinterest = serializers.ChoiceField(
        # label=_('Area of Interest'),
        choices=AREA_OF_INTERESTS
    )
    role = serializers.ChoiceField(
        choices=CACIP_USER_ROLE_VALUES
    )

    def validate_country(self, country):
        country = get_adapter().clean_country(country)
        return country

    def validate_areaofinterest(self, areaofinterest):
        areaofinterest = get_adapter().clean_areaofinterest(areaofinterest)
        return areaofinterest

    def validate_role(self, role):
        role = get_adapter().clean_role(role)
        return role

    def get_cleaned_data(self):
        result = super(CustomRegisterSerializer, self).get_cleaned_data()
        result.update({
            'country': self.validated_data.get('country', ''),
            'areaofinterest': self.validated_data.get('areaofinterest', ''),
            'role': self.validated_data.get('role', '')
        })
        return result
