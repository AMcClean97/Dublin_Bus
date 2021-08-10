# Generated by Django 3.2.5 on 2021-08-10 20:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Bus', '0002_auto_20210725_1847'),
    ]

    operations = [
        migrations.CreateModel(
            name='WeatherPrediction',
            fields=[
                ('dt', models.IntegerField(primary_key=True, serialize=False)),
                ('temp', models.FloatField(blank=True, null=True)),
                ('feels_like', models.FloatField(blank=True, null=True)),
                ('temp_min', models.FloatField(blank=True, null=True)),
                ('temp_max', models.FloatField(blank=True, null=True)),
                ('humidity', models.FloatField(blank=True, null=True)),
                ('wind_speed', models.FloatField(blank=True, null=True)),
                ('weather_main', models.CharField(blank=True, max_length=30, null=True)),
                ('weather_description', models.CharField(blank=True, max_length=60, null=True)),
                ('weather_icon', models.CharField(blank=True, max_length=10, null=True)),
            ],
            options={
                'db_table': 'weather_predictions',
                'managed': False,
            },
        ),
    ]