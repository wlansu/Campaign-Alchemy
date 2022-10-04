# Generated by Django 4.1.1 on 2022-10-03 09:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0002_remove_location_image_remove_location_thumbnail'),
        ('characters', '0003_character_is_npc'),
    ]

    operations = [
        migrations.AlterField(
            model_name='character',
            name='location',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='characters', to='locations.location'),
        ),
    ]