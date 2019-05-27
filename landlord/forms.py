from django.forms import ModelForm
from .models import Rent, Charge
from datetime import timedelta, datetime


class NewRentForm(ModelForm):
    class Meta:
        model = Rent
        fields = ['name']


class NewChargeForm(ModelForm):

    #custom validator to ensure recurring date is after due date,
    #due date is after today
    def clean(self):
        cleaned_data = super(NewChargeForm, self).clean()
        due_date = cleaned_data.get('due_date')
        recurring_until = cleaned_data.get('recurring_until')
        recurring = cleaned_data.get('recurring')
        if due_date and recurring_until:
            if recurring_until < (due_date + timedelta(days=31)):
                self.add_error('recurring_until',
                               ('Recurring until date must be at least '
                                '31 days after the due date'))
            if recurring_until and not recurring:
                self.add_error('recurring_until',
                               ("you can't set a recurring until "
                                "date for one time charges"))
        if due_date and due_date < (datetime.now().date() + timedelta(days=1)):
            self.add_error(
                'due_date',
                "please select a date at least one day after today")

        if recurring and not recurring_until:
            self.add_error('recurring_until',
                           'please enter a recurring until date')

    class Meta:
        model = Charge
        fields = [
            'amount', 'title', 'recurring', 'due_date', 'recurring_until'
        ]
