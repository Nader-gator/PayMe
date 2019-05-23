from django.db import models
from users.models import User
from landlord.models import Rent


class Renter(models.Model):
    profile = models.OneToOneField(to=User,
                                   on_delete=models.CASCADE,
                                   related_name='renter_profile')
    rent = models.ForeignKey(
        to=Rent,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
