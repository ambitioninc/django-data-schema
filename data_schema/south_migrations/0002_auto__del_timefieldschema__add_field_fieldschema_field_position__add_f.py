# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'TimeFieldSchema'
        db.delete_table(u'data_schema_timefieldschema')

        # Adding field 'FieldSchema.field_position'
        db.add_column(u'data_schema_fieldschema', 'field_position',
                      self.gf('django.db.models.fields.IntegerField')(null=True),
                      keep_default=False)

        # Adding field 'FieldSchema.field_type'
        db.add_column(u'data_schema_fieldschema', 'field_type',
                      self.gf('django.db.models.fields.CharField')(default=0, max_length=32),
                      keep_default=False)

        # Adding field 'FieldSchema.field_format'
        db.add_column(u'data_schema_fieldschema', 'field_format',
                      self.gf('django.db.models.fields.CharField')(default=None, max_length=64, null=True, blank=True),
                      keep_default=False)


        # Changing field 'FieldSchema.uniqueness_order'
        db.alter_column(u'data_schema_fieldschema', 'uniqueness_order', self.gf('django.db.models.fields.IntegerField')(null=True))

    def backwards(self, orm):
        # Adding model 'TimeFieldSchema'
        db.create_table(u'data_schema_timefieldschema', (
            (u'fieldschema_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['data_schema.FieldSchema'], unique=True, primary_key=True)),
        ))
        db.send_create_signal(u'data_schema', ['TimeFieldSchema'])

        # Deleting field 'FieldSchema.field_position'
        db.delete_column(u'data_schema_fieldschema', 'field_position')

        # Deleting field 'FieldSchema.field_type'
        db.delete_column(u'data_schema_fieldschema', 'field_type')

        # Deleting field 'FieldSchema.field_format'
        db.delete_column(u'data_schema_fieldschema', 'field_format')


        # Changing field 'FieldSchema.uniqueness_order'
        db.alter_column(u'data_schema_fieldschema', 'uniqueness_order', self.gf('django.db.models.fields.PositiveIntegerField')(null=True))

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
            'field_format': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'field_key': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'field_position': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'field_type': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'uniqueness_order': ('django.db.models.fields.IntegerField', [], {'null': 'True'})
        }
    }

    complete_apps = ['data_schema']