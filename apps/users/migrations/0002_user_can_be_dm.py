# Generated by Django 3.2.13 on 2022-07-01 20:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='can_be_dm',
            field=models.BooleanField(default=True),
        ),
    ]
