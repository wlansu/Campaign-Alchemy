# Generated by Django 4.1.1 on 2022-10-14 21:06

from django.db import migrations
import tinymce.models


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0004_location_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='description',
            field=tinymce.models.HTMLField(blank=True),
        ),
    ]
