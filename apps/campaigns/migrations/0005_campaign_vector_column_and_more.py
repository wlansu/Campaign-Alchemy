# Generated by Django 4.1.1 on 2022-10-04 14:46

import django.contrib.postgres.indexes
import django.contrib.postgres.search
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('campaigns', '0004_campaign_invite_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='campaign',
            name='vector_column',
            field=django.contrib.postgres.search.SearchVectorField(null=True),
        ),
        migrations.AddIndex(
            model_name='campaign',
            index=django.contrib.postgres.indexes.GinIndex(fields=['vector_column'], name='campaigns_c_vector__a8e39c_gin'),
        ),
    ]