# Generated by Django 2.2.1 on 2019-05-27 05:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='is_landlord',
            field=models.BooleanField(default=False, verbose_name='Check here if you are a landlord'),
        ),
    ]
