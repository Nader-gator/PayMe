from django.forms import ModelForm
from .models import Rent, Charge


class NewRentForm(ModelForm):
    class Meta:
        model = Rent
        fields = ['name']


class NewChargeForm(ModelForm):
    class Meta:
        model = Charge
        fields = ['title', 'category', 'due_date', 'recurring_until']
