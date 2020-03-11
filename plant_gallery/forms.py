from django import forms
from . models import Lighting, Type, Plant, Payment



class LightingForm(forms.Form):

    lighting_field = forms.ModelChoiceField(queryset=Lighting.objects.all(), to_field_name="lighting_condition")


class TypeForm(forms.Form):

    type_field = forms.ModelChoiceField(queryset=Type.objects.all(), to_field_name="plant_type")


class PlantForm(forms.ModelForm):
    class Meta:
        model = Plant
        fields = ['name', 'description', 'cost', 'for_sale']
        labels = {'name': 'Nickname: ', 'description': 'Description: ',
                  'cost': 'Cost', 'for_sale': 'Plant For Sale'}


token_choices = (
    (100, "100 PlantTokens for 4.99"),
    (250, "250 PlantTokens for 9.99"),
    (500, "500 PlantTokens for 14.99"),
    (1000, "1000 PlantTokens for 29.99")
)


class PaymentForm(forms.ModelForm):

    amount = forms.ChoiceField(choices=token_choices)


    class Meta:
        model = Payment
        fields = ['first_name', 'last_name', 'card_number', 'security_code', 'exp_month',
                  'exp_year', 'zip', 'amount']
        labels = {'first_name': 'First Name: ', 'last_name': 'Last Name: ', 'card_number': 'Card Number: ',
                  'security_code': 'Security Code: ', 'exp_month': 'Expiration Month: ',
                  'exp_year': 'Expiration Year: ', 'zip': 'Zip: ', 'amount': 'Amount:'}



