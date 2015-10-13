# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data_schema', '0002_auto_20150705_1714'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fieldoption',
            name='value',
            field=models.CharField(max_length=1024),
        ),
    ]
