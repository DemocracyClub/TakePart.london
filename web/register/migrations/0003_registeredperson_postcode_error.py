# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-05-25 13:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('register', '0002_auto_20160525_1307'),
    ]

    operations = [
        migrations.AddField(
            model_name='registeredperson',
            name='postcode_error',
            field=models.BooleanField(default=False),
        ),
    ]