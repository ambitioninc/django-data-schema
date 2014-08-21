# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'FieldOption'
        db.create_table(u'data_schema_fieldoption', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('field_schema', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['data_schema.FieldSchema'])),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=128)),
        ))
        db.send_create_signal(u'data_schema', ['FieldOption'])

        # Adding field 'FieldSchema.has_options'
        db.add_column(u'data_schema_fieldschema', 'has_options',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'FieldOption'
        db.delete_table(u'data_schema_fieldoption')

        # Deleting field 'FieldSchema.has_options'
        db.delete_column(u'data_schema_fieldschema', 'has_options')


    models = {
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'data_schema.dataschema': {
            'Meta': {'object_name': 'DataSchema'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model_content_type': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['contenttypes.ContentType']", 'null': 'True'})
        },
        u'data_schema.fieldoption': {
            'Meta': {'object_name': 'FieldOption'},
            'field_schema': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['data_schema.FieldSchema']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        u'data_schema.fieldschema': {
            'Meta': {'unique_together': "(('data_schema', 'field_key'),)", 'object_name': 'FieldSchema'},
            'data_schema': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['data_schema.DataSchema']"}),
            'default_value': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'display_name': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '64', 'null': 'True'}),
            'field_format': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'field_key': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'field_position': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'field_type': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'has_options': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'uniqueness_order': ('django.db.models.fields.IntegerField', [], {'null': 'True'})
        }
    }

    complete_apps = ['data_schema']