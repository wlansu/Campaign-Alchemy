# Generated by Django 4.1.1 on 2022-11-04 20:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('characters', '0011_character_creator_alter_character_player'),
    ]

    operations = [
        migrations.AlterField(
            model_name='character',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='characters/'),
        ),
    ]