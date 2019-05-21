from django.db import models
from landlord.models import Landlord


class Rent(models.Model):
    landlord = models.ForeignKey(to=Landlord, on_delete=models.CASCADE)


class Charge(models.Model):
    one_time = 'ot'
    recurring = 'rc'
    choice_types = [
        (one_time, 'One Time'),
        (recurring, 'Recurring'),
    ]

    rent = models.ForeignKey(to=Rent, on_delete=models.PROTECT)
    category = models.CharField(max_length=2,
                                choices=choice_types,
                                default=one_time)
    due_date = models.DateField()
    recurring_until = models.DateField(null=True, blank=True)
    active = models.BooleanField(default=True)
    paid = models.BooleanField(default=False)
