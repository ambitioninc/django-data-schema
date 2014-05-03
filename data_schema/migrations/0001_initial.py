# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'DataSchema'
        db.create_table(u'data_schema_dataschema', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('model_content_type', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['contenttypes.ContentType'], null=True)),
        ))
        db.send_create_signal(u'data_schema', ['DataSchema'])

        # Adding model 'FieldSchema'
        db.create_table(u'data_schema_fieldschema', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('data_schema', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['data_schema.DataSchema'])),
            ('field_key', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('uniqueness_order', self.gf('django.db.models.fields.PositiveIntegerField')(null=True)),
        ))
        db.send_create_signal(u'data_schema', ['FieldSchema'])

        # Adding unique constraint on 'FieldSchema', fields ['data_schema', 'field_key']
        db.create_unique(u'data_schema_fieldschema', ['data_schema_id', 'field_key'])

        # Adding model 'TimeFieldSchema'
        db.create_table(u'data_schema_timefieldschema', (
            (u'fieldschema_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['data_schema.FieldSchema'], unique=True, primary_key=True)),
        ))
        db.send_create_signal(u'data_schema', ['TimeFieldSchema'])


    def backwards(self, orm):
        # Removing unique constraint on 'FieldSchema', fields ['data_schema', 'field_key']
        db.delete_unique(u'data_schema_fieldschema', ['data_schema_id', 'field_key'])

        # Deleting model 'DataSchema'
        db.delete_table(u'data_schema_dataschema')

        # Deleting model 'FieldSchema'
        db.delete_table(u'data_schema_fieldschema')

        # Deleting model 'TimeFieldSchema'
        db.delete_table(u'data_schema_timefieldschema')


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
            'field_key': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'uniqueness_order': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'})
        },
        u'data_schema.timefieldschema': {
            'Meta': {'object_name': 'TimeFieldSchema', '_ormbases': [u'data_schema.FieldSchema']},
            u'fieldschema_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['data_schema.FieldSchema']", 'unique': 'True', 'primary_key': 'True'})
        }
    }

    complete_apps = ['data_schema']