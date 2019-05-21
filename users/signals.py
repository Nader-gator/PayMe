from renter.models import Renter
from landlord.models import Landlord
from users.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save


@receiver(post_save, sender=User)
def create_relation(sender, instance, created, **kwargs):
    if created:
        if instance.is_landlord:
            Landlord.objects.create(profile=instance)
        else:
            Renter.objects.create(profile=instance)
