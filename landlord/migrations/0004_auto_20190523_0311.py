# Generated by Django 2.2.1 on 2019-05-23 03:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('landlord', '0003_auto_20190523_0155'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='charge',
            name='category',
        ),
        migrations.AddField(
            model_name='charge',
            name='recurring',
            field=models.BooleanField(default=False),
        ),
    ]
