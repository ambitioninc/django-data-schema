# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data_schema', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fieldschema',
            name='display_name',
            field=models.CharField(default=b'', max_length=64, blank=True),
        ),
        migrations.AlterUniqueTogether(
            name='fieldoption',
            unique_together=set([('field_schema', 'value')]),
        ),
    ]
