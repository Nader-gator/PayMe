# Generated by Django 2.2.1 on 2019-05-23 01:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('landlord', '0002_auto_20190523_0124'),
    ]

    operations = [
        migrations.AlterField(
            model_name='charge',
            name='title',
            field=models.CharField(max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='rent',
            name='name',
            field=models.CharField(max_length=255),
        ),
    ]