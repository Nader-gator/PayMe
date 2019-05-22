# Generated by Django 2.2.1 on 2019-05-22 00:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Charge',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(choices=[('ot', 'One Time'), ('rc', 'Recurring')], default='ot', max_length=2)),
                ('due_date', models.DateField()),
                ('recurring_until', models.DateField(blank=True, null=True)),
                ('active', models.BooleanField(default=True)),
                ('paid', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Landlord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Rent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('landlord', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='landlord.Landlord')),
            ],
        ),
    ]
