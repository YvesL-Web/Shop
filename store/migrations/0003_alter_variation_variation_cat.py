# Generated by Django 4.2.2 on 2023-06-23 13:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_alter_variation_variation_cat'),
    ]

    operations = [
        migrations.AlterField(
            model_name='variation',
            name='variation_cat',
            field=models.CharField(choices=[('size', 'size'), ('color', 'color')], max_length=100),
        ),
    ]