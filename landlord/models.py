from django.db import models
from users.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Landlord(models.Model):
    profile = models.OneToOneField(to=User,
                                   on_delete=models.CASCADE,
                                   related_name='landlord_profile')


class Rent(models.Model):
    landlord = models.ForeignKey(to=Landlord, on_delete=models.CASCADE)
    name = models.CharField(
        max_length=255,
        null=False,
        blank=False,
    )


class Charge(models.Model):
    rent = models.ForeignKey(to=Rent, on_delete=models.PROTECT)
    title = models.CharField(
        max_length=255,
        unique=True,
        null=False,
        blank=False,
    )
    recurring = models.BooleanField(default=False)
    due_date = models.DateField()
    recurring_until = models.DateField(null=True, blank=True)
    active = models.BooleanField(default=True)
    paid = models.BooleanField(default=False)
    amount = models.IntegerField(
        validators=[MinValueValidator(0),
                    MaxValueValidator(100000)])
    last_month_paid = models.IntegerField()
