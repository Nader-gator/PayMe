from django.db import models
from users.models import User


class Landlord(models.Model):
    profile = models.OneToOneField(to=User, on_delete=models.CASCADE)
