# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-06 16:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('register', '0021_auto_20160530_0608'),
    ]

    operations = [
        migrations.AddField(
            model_name='llsoa',
            name='population_2014',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='llsoa',
            name='population_voting_age_2014',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='llsoa',
            name='population_young_2014',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]