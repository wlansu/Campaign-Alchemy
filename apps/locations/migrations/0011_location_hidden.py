# Generated by Django 4.1.4 on 2022-12-17 13:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0010_alter_location_options_location_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='hidden',
            field=models.BooleanField(default=False),
        ),
    ]