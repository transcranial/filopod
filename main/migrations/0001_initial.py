# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Domain'
        db.create_table('main_domain', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('datetime_added', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('main', ['Domain'])

        # Adding model 'Ontology'
        db.create_table('main_ontology', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('datetime_added', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('main', ['Ontology'])

        # Adding M2M table for field domain on 'Ontology'
        db.create_table('main_ontology_domain', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('ontology', models.ForeignKey(orm['main.ontology'], null=False)),
            ('domain', models.ForeignKey(orm['main.domain'], null=False))
        ))
        db.create_unique('main_ontology_domain', ['ontology_id', 'domain_id'])

        # Adding model 'Concept'
        db.create_table('main_concept', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('ontology', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Ontology'], null=True, blank=True)),
            ('conceptID', self.gf('django.db.models.fields.CharField')(max_length=255, unique=True, null=True, blank=True)),
            ('datetime_added', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('main', ['Concept'])

        # Adding model 'Term'
        db.create_table('main_term', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('concept', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Concept'])),
            ('datetime_added', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('main', ['Term'])

        # Adding model 'ConceptConceptLink'
        db.create_table('main_conceptconceptlink', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('source_concept', self.gf('django.db.models.fields.related.ForeignKey')(related_name='source', to=orm['main.Concept'])),
            ('target_concept', self.gf('django.db.models.fields.related.ForeignKey')(related_name='target', to=orm['main.Concept'])),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('value', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=10, decimal_places=9)),
            ('datetime_added', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('main', ['ConceptConceptLink'])

        # Adding model 'Resource'
        db.create_table('main_resource', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('identifier', self.gf('django.db.models.fields.CharField')(max_length=500, null=True, blank=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('language', self.gf('django.db.models.fields.CharField')(max_length=2, null=True, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=300, null=True, blank=True)),
            ('date', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('publisher', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('author', self.gf('django.db.models.fields.CharField')(max_length=767, null=True, blank=True)),
            ('journal', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('volume', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('issue', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('firstpage', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('lastpage', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('html_source', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('datetime_added', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('main', ['Resource'])

        # Adding M2M table for field user on 'Resource'
        db.create_table('main_resource_user', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('resource', models.ForeignKey(orm['main.resource'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('main_resource_user', ['resource_id', 'user_id'])

        # Adding M2M table for field domain on 'Resource'
        db.create_table('main_resource_domain', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('resource', models.ForeignKey(orm['main.resource'], null=False)),
            ('domain', models.ForeignKey(orm['main.domain'], null=False))
        ))
        db.create_unique('main_resource_domain', ['resource_id', 'domain_id'])

        # Adding model 'Subresource'
        db.create_table('main_subresource', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('containing_resource', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Resource'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('content', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('file', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('datetime_added', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('main', ['Subresource'])

        # Adding M2M table for field concepts_contained on 'Subresource'
        db.create_table('main_subresource_concepts_contained', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('subresource', models.ForeignKey(orm['main.subresource'], null=False)),
            ('concept', models.ForeignKey(orm['main.concept'], null=False))
        ))
        db.create_unique('main_subresource_concepts_contained', ['subresource_id', 'concept_id'])

        # Adding model 'ConceptSubresourceLink'
        db.create_table('main_conceptsubresourcelink', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('concept', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Concept'])),
            ('subresource', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Subresource'])),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('value', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('datetime_added', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('main', ['ConceptSubresourceLink'])

        # Adding model 'QueuedResProcessTask'
        db.create_table('main_queuedresprocesstask', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('taskID', self.gf('django.db.models.fields.CharField')(max_length=64)),
        ))
        db.send_create_signal('main', ['QueuedResProcessTask'])


    def backwards(self, orm):
        # Deleting model 'Domain'
        db.delete_table('main_domain')

        # Deleting model 'Ontology'
        db.delete_table('main_ontology')

        # Removing M2M table for field domain on 'Ontology'
        db.delete_table('main_ontology_domain')

        # Deleting model 'Concept'
        db.delete_table('main_concept')

        # Deleting model 'Term'
        db.delete_table('main_term')

        # Deleting model 'ConceptConceptLink'
        db.delete_table('main_conceptconceptlink')

        # Deleting model 'Resource'
        db.delete_table('main_resource')

        # Removing M2M table for field user on 'Resource'
        db.delete_table('main_resource_user')

        # Removing M2M table for field domain on 'Resource'
        db.delete_table('main_resource_domain')

        # Deleting model 'Subresource'
        db.delete_table('main_subresource')

        # Removing M2M table for field concepts_contained on 'Subresource'
        db.delete_table('main_subresource_concepts_contained')

        # Deleting model 'ConceptSubresourceLink'
        db.delete_table('main_conceptsubresourcelink')

        # Deleting model 'QueuedResProcessTask'
        db.delete_table('main_queuedresprocesstask')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'main.concept': {
            'Meta': {'object_name': 'Concept'},
            'conceptID': ('django.db.models.fields.CharField', [], {'max_length': '255', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'datetime_added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'ontology': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Ontology']", 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'main.conceptconceptlink': {
            'Meta': {'object_name': 'ConceptConceptLink'},
            'datetime_added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'source_concept': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'source'", 'to': "orm['main.Concept']"}),
            'target_concept': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'target'", 'to': "orm['main.Concept']"}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'value': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '10', 'decimal_places': '9'})
        },
        'main.conceptsubresourcelink': {
            'Meta': {'object_name': 'ConceptSubresourceLink'},
            'concept': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Concept']"}),
            'datetime_added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'subresource': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Subresource']"}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'value': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        'main.domain': {
            'Meta': {'object_name': 'Domain'},
            'datetime_added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        'main.ontology': {
            'Meta': {'object_name': 'Ontology'},
            'datetime_added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'domain': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['main.Domain']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        'main.queuedresprocesstask': {
            'Meta': {'object_name': 'QueuedResProcessTask'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'taskID': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'main.resource': {
            'Meta': {'object_name': 'Resource'},
            'author': ('django.db.models.fields.CharField', [], {'max_length': '767', 'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'datetime_added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'domain': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['main.Domain']", 'null': 'True', 'blank': 'True'}),
            'firstpage': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'html_source': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identifier': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            'issue': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'journal': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'lastpage': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'publisher': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '300', 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'volume': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'})
        },
        'main.subresource': {
            'Meta': {'object_name': 'Subresource'},
            'concepts_contained': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['main.Concept']", 'null': 'True', 'blank': 'True'}),
            'containing_resource': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Resource']"}),
            'content': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'datetime_added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'main.term': {
            'Meta': {'object_name': 'Term'},
            'concept': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Concept']"}),
            'datetime_added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        }
    }

    complete_apps = ['main']