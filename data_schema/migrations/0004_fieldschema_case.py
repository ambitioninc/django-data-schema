# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-07-13 20:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_schema', '0003_auto_20151013_1556'),
    ]

    operations = [
        migrations.AddField(
            model_name='fieldschema',
            name='transform_case',
            field=models.CharField(blank=True, default=None, max_length=5, null=True),
        ),
    ]
