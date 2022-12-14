# Generated by Django 4.1.1 on 2022-09-13 20:03

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('maps', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('image', models.ImageField(null=True, upload_to='locations/')),
                ('thumbnail', models.ImageField(null=True, upload_to='locations/thumbnails/')),
                ('longitude', models.FloatField(default=0)),
                ('latitude', models.FloatField(default=0)),
                ('map', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='locations', to='maps.map')),
            ],
            options={
                'verbose_name': 'Location',
                'verbose_name_plural': 'Locations',
            },
        ),
    ]
