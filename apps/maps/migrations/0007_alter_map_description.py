# Generated by Django 4.1.1 on 2022-10-14 21:06

from django.db import migrations
import tinymce.models


class Migration(migrations.Migration):

    dependencies = [
        ('maps', '0006_map_maps_map_name_c173ad_idx'),
    ]

    operations = [
        migrations.AlterField(
            model_name='map',
            name='description',
            field=tinymce.models.HTMLField(blank=True),
        ),
    ]
