from django import forms
from django.forms.widgets import Select
from allauth.account.views import SignupView, SignupForm
from allauth.utils import set_form_field_order
from geonode.people.enumerations import AREA_OF_INTERESTS, CACIP_USER_ROLE_VALUES
from geonode.base.enumerations import COUNTRIES
from django.utils.translation import ugettext_lazy as _
from geonode.base.models import TopicCategory

class CustomSignupForm(SignupForm):
    country = forms.ChoiceField(
        choices=COUNTRIES
    )
    areaofinterest = forms.ChoiceField(
        label=_('Area of Interest'),
        choices=TopicCategory.objects.values_list('id','gn_description')
    )
    role = forms.ChoiceField(
        choices=CACIP_USER_ROLE_VALUES
    )
    def __init__(self, *args, **kwargs):
        super(CustomSignupForm, self).__init__(*args, **kwargs)
        default_field_order = [
            'username',
            'email',
            'email2',  # ignored when not present
            'country',
            'areaofinterest',
            'role',
            'password1',
            'password2'  # ignored when not present
        ]
        set_form_field_order(
            self,
            getattr(self, 'field_order', None) or default_field_order)

class CustomSignupView(SignupView):
    form_class = CustomSignupForm

signup = CustomSignupView.as_view()
