# Generated by Django 2.2.1 on 2019-05-21 22:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('charges', '0001_initial'),
        ('renter', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='renter',
            name='rent',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='charges.Rent'),
        ),
        migrations.AlterField(
            model_name='renter',
            name='profile',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='renter_profile', to=settings.AUTH_USER_MODEL),
        ),
    ]
