# Generated by Django 2.2.28 on 2022-08-18 14:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_schema', '0005_auto_20180302_2356'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fieldschema',
            name='display_name',
            field=models.TextField(blank=True, default=''),
        ),
    ]
