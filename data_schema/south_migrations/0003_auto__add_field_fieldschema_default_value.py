# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'FieldSchema.default_value'
        db.add_column(u'data_schema_fieldschema', 'default_value',
                      self.gf('django.db.models.fields.CharField')(default=None, max_length=128, null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'FieldSchema.default_value'
        db.delete_column(u'data_schema_fieldschema', 'default_value')


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
        u'data_schema.fieldschema': {
            'Meta': {'unique_together': "(('data_schema', 'field_key'),)", 'object_name': 'FieldSchema'},
            'data_schema': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['data_schema.DataSchema']"}),
            'default_value': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'field_format': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'field_key': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'field_position': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'field_type': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'uniqueness_order': ('django.db.models.fields.IntegerField', [], {'null': 'True'})
        }
    }

    complete_apps = ['data_schema']