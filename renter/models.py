from django.db import models
from landlord.models import Rent
from django.conf import settings


class Renter(models.Model):
    profile = models.OneToOneField(to=settings.AUTH_USER_MODEL,
                                   on_delete=models.CASCADE,
                                   related_name='renter_profile')
    rent = models.ForeignKey(
        to=Rent,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
