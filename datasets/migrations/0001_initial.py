# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'DataSet'
        db.create_table('datasets_dataset', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ark_key', self.gf('django.db.models.fields.CharField')(max_length=500, blank=True)),
        ))
        db.send_create_signal('datasets', ['DataSet'])

        # Adding model 'Keys'
        db.create_table('datasets_keys', (
            ('key_name', self.gf('django.db.models.fields.CharField')(max_length=1000, primary_key=True)),
            ('public', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('datasets', ['Keys'])

        # Adding model 'KeyValues'
        db.create_table('datasets_keyvalues', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('dataset', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['datasets.DataSet'])),
            ('key', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['datasets.Keys'])),
            ('value', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('datasets', ['KeyValues'])


    def backwards(self, orm):
        # Deleting model 'DataSet'
        db.delete_table('datasets_dataset')

        # Deleting model 'Keys'
        db.delete_table('datasets_keys')

        # Deleting model 'KeyValues'
        db.delete_table('datasets_keyvalues')


    models = {
        'datasets.dataset': {
            'Meta': {'object_name': 'DataSet'},
            'ark_key': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'datasets.keys': {
            'Meta': {'object_name': 'Keys'},
            'key_name': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'primary_key': 'True'}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'datasets.keyvalues': {
            'Meta': {'object_name': 'KeyValues'},
            'dataset': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['datasets.DataSet']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['datasets.Keys']"}),
            'value': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        }
    }

    complete_apps = ['datasets']