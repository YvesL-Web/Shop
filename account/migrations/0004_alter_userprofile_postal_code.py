# Generated by Django 4.2.2 on 2023-06-29 11:37

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0003_alter_userprofile_postal_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='postal_code',
            field=models.CharField(blank=True, max_length=6, null=True, validators=[django.core.validators.RegexValidator('^[0-9]$', 'Invalid postal code')]),
        ),
    ]
