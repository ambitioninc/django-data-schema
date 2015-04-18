# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DataSchema',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('model_content_type', models.ForeignKey(default=None, to='contenttypes.ContentType', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FieldOption',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.CharField(max_length=128)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FieldSchema',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('field_key', models.CharField(max_length=64)),
                ('display_name', models.CharField(default=None, max_length=64, null=True)),
                ('uniqueness_order', models.IntegerField(null=True)),
                ('field_position', models.IntegerField(null=True)),
                ('field_format', models.CharField(default=None, max_length=64, null=True, blank=True)),
                ('default_value', models.CharField(default=None, max_length=128, null=True, blank=True)),
                ('field_type', models.CharField(choices=[('BOOLEAN', 'BOOLEAN'), ('DATE', 'DATE'), ('DATETIME', 'DATETIME'), ('FLOAT', 'FLOAT'), ('INT', 'INT'), ('STRING', 'STRING')], max_length=32)),
                ('has_options', models.BooleanField(default=False)),
                ('data_schema', models.ForeignKey(to='data_schema.DataSchema')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='fieldschema',
            unique_together=set([('data_schema', 'field_key')]),
        ),
        migrations.AddField(
            model_name='fieldoption',
            name='field_schema',
            field=models.ForeignKey(to='data_schema.FieldSchema'),
            preserve_default=True,
        ),
    ]
