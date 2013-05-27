# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Station'
        db.create_table(u'skyscanner_scraper_station', (
            ('code', self.gf('django.db.models.fields.CharField')(max_length=80, primary_key=True)),
            ('id', self.gf('django.db.models.fields.IntegerField')(default=None, null=True, db_index=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(default=None, max_length=80, null=True, blank=True)),
        ))
        db.send_create_signal(u'skyscanner_scraper', ['Station'])

        # Adding model 'Carrier'
        db.create_table(u'skyscanner_scraper_carrier', (
            ('id', self.gf('django.db.models.fields.CharField')(max_length=5, primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=80)),
        ))
        db.send_create_signal(u'skyscanner_scraper', ['Carrier'])

        # Adding model 'Agent'
        db.create_table(u'skyscanner_scraper_agent', (
            ('id', self.gf('django.db.models.fields.CharField')(max_length=10, primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('default_url', self.gf('django.db.models.fields.URLField')(max_length=255)),
            ('booking_number', self.gf('django.db.models.fields.CharField')(max_length=80, null=True, blank=True)),
            ('is_carrier', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'skyscanner_scraper', ['Agent'])

        # Adding model 'Quote'
        db.create_table(u'skyscanner_scraper_quote', (
            ('id', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
            ('price', self.gf('django.db.models.fields.DecimalField')(max_digits=8, decimal_places=2)),
            ('request_time', self.gf('django.db.models.fields.DateTimeField')()),
            ('agent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['skyscanner_scraper.Agent'])),
            ('is_return', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True)),
        ))
        db.send_create_signal(u'skyscanner_scraper', ['Quote'])

        # Adding model 'PricingOption'
        db.create_table(u'skyscanner_scraper_pricingoption', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('quote', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['skyscanner_scraper.Quote'], blank=True)),
            ('inbound_flight', self.gf('django.db.models.fields.related.ForeignKey')(default=None, related_name='inbound_priceoption_set', null=True, blank=True, to=orm['skyscanner_scraper.Flight'])),
            ('outbound_flight', self.gf('django.db.models.fields.related.ForeignKey')(default=None, related_name='outbound_priceoption_set', null=True, blank=True, to=orm['skyscanner_scraper.Flight'])),
        ))
        db.send_create_signal(u'skyscanner_scraper', ['PricingOption'])

        # Adding model 'QueryFlight'
        db.create_table(u'skyscanner_scraper_queryflight', (
            ('request_id', self.gf('django.db.models.fields.CharField')(max_length=80, primary_key=True)),
            ('outbound_date', self.gf('django.db.models.fields.DateField')()),
            ('inbound_date', self.gf('django.db.models.fields.DateField')(default=None, null=True, blank=True)),
        ))
        db.send_create_signal(u'skyscanner_scraper', ['QueryFlight'])

        # Adding M2M table for field origin_station_set on 'QueryFlight'
        m2m_table_name = db.shorten_name(u'skyscanner_scraper_queryflight_origin_station_set')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('queryflight', models.ForeignKey(orm[u'skyscanner_scraper.queryflight'], null=False)),
            ('station', models.ForeignKey(orm[u'skyscanner_scraper.station'], null=False))
        ))
        db.create_unique(m2m_table_name, ['queryflight_id', 'station_id'])

        # Adding M2M table for field destination_station_set on 'QueryFlight'
        m2m_table_name = db.shorten_name(u'skyscanner_scraper_queryflight_destination_station_set')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('queryflight', models.ForeignKey(orm[u'skyscanner_scraper.queryflight'], null=False)),
            ('station', models.ForeignKey(orm[u'skyscanner_scraper.station'], null=False))
        ))
        db.create_unique(m2m_table_name, ['queryflight_id', 'station_id'])

        # Adding model 'Flight'
        db.create_table(u'skyscanner_scraper_flight', (
            ('id', self.gf('django.db.models.fields.CharField')(max_length=100, primary_key=True)),
            ('inbound_itinerary_leg', self.gf('django.db.models.fields.BooleanField')(default=True, db_index=True)),
            ('origin_station', self.gf('django.db.models.fields.related.ForeignKey')(default=None, related_name='origin_flight_set', null=True, blank=True, to=orm['skyscanner_scraper.Station'])),
            ('destination_station', self.gf('django.db.models.fields.related.ForeignKey')(default=None, related_name='destination_flight_set', null=True, blank=True, to=orm['skyscanner_scraper.Station'])),
            ('departure_time', self.gf('django.db.models.fields.DateTimeField')(default=None, null=True, blank=True)),
            ('arrival_time', self.gf('django.db.models.fields.DateTimeField')(default=None, null=True, blank=True)),
            ('duration', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('stop_count', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('query_flight', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['skyscanner_scraper.QueryFlight'])),
        ))
        db.send_create_signal(u'skyscanner_scraper', ['Flight'])

        # Adding M2M table for field stop_station_set on 'Flight'
        m2m_table_name = db.shorten_name(u'skyscanner_scraper_flight_stop_station_set')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('flight', models.ForeignKey(orm[u'skyscanner_scraper.flight'], null=False)),
            ('station', models.ForeignKey(orm[u'skyscanner_scraper.station'], null=False))
        ))
        db.create_unique(m2m_table_name, ['flight_id', 'station_id'])

        # Adding M2M table for field carrier_set on 'Flight'
        m2m_table_name = db.shorten_name(u'skyscanner_scraper_flight_carrier_set')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('flight', models.ForeignKey(orm[u'skyscanner_scraper.flight'], null=False)),
            ('carrier', models.ForeignKey(orm[u'skyscanner_scraper.carrier'], null=False))
        ))
        db.create_unique(m2m_table_name, ['flight_id', 'carrier_id'])


    def backwards(self, orm):
        # Deleting model 'Station'
        db.delete_table(u'skyscanner_scraper_station')

        # Deleting model 'Carrier'
        db.delete_table(u'skyscanner_scraper_carrier')

        # Deleting model 'Agent'
        db.delete_table(u'skyscanner_scraper_agent')

        # Deleting model 'Quote'
        db.delete_table(u'skyscanner_scraper_quote')

        # Deleting model 'PricingOption'
        db.delete_table(u'skyscanner_scraper_pricingoption')

        # Deleting model 'QueryFlight'
        db.delete_table(u'skyscanner_scraper_queryflight')

        # Removing M2M table for field origin_station_set on 'QueryFlight'
        db.delete_table(db.shorten_name(u'skyscanner_scraper_queryflight_origin_station_set'))

        # Removing M2M table for field destination_station_set on 'QueryFlight'
        db.delete_table(db.shorten_name(u'skyscanner_scraper_queryflight_destination_station_set'))

        # Deleting model 'Flight'
        db.delete_table(u'skyscanner_scraper_flight')

        # Removing M2M table for field stop_station_set on 'Flight'
        db.delete_table(db.shorten_name(u'skyscanner_scraper_flight_stop_station_set'))

        # Removing M2M table for field carrier_set on 'Flight'
        db.delete_table(db.shorten_name(u'skyscanner_scraper_flight_carrier_set'))


    models = {
        u'skyscanner_scraper.agent': {
            'Meta': {'object_name': 'Agent'},
            'booking_number': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'default_url': ('django.db.models.fields.URLField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '10', 'primary_key': 'True'}),
            'is_carrier': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'skyscanner_scraper.carrier': {
            'Meta': {'object_name': 'Carrier'},
            'id': ('django.db.models.fields.CharField', [], {'max_length': '5', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'})
        },
        u'skyscanner_scraper.flight': {
            'Meta': {'object_name': 'Flight'},
            'arrival_time': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'carrier_set': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['skyscanner_scraper.Carrier']", 'symmetrical': 'False'}),
            'departure_time': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'destination_station': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'destination_flight_set'", 'null': 'True', 'blank': 'True', 'to': u"orm['skyscanner_scraper.Station']"}),
            'duration': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '100', 'primary_key': 'True'}),
            'inbound_itinerary_leg': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'origin_station': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'origin_flight_set'", 'null': 'True', 'blank': 'True', 'to': u"orm['skyscanner_scraper.Station']"}),
            'query_flight': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['skyscanner_scraper.QueryFlight']"}),
            'stop_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'stop_station_set': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['skyscanner_scraper.Station']", 'symmetrical': 'False'})
        },
        u'skyscanner_scraper.pricingoption': {
            'Meta': {'object_name': 'PricingOption'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inbound_flight': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'inbound_priceoption_set'", 'null': 'True', 'blank': 'True', 'to': u"orm['skyscanner_scraper.Flight']"}),
            'outbound_flight': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'outbound_priceoption_set'", 'null': 'True', 'blank': 'True', 'to': u"orm['skyscanner_scraper.Flight']"}),
            'quote': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['skyscanner_scraper.Quote']", 'blank': 'True'})
        },
        u'skyscanner_scraper.queryflight': {
            'Meta': {'object_name': 'QueryFlight'},
            'destination_station_set': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'destination_queryflight_set'", 'symmetrical': 'False', 'to': u"orm['skyscanner_scraper.Station']"}),
            'inbound_date': ('django.db.models.fields.DateField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'origin_station_set': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'origin_queryflight_set'", 'symmetrical': 'False', 'to': u"orm['skyscanner_scraper.Station']"}),
            'outbound_date': ('django.db.models.fields.DateField', [], {}),
            'request_id': ('django.db.models.fields.CharField', [], {'max_length': '80', 'primary_key': 'True'})
        },
        u'skyscanner_scraper.quote': {
            'Meta': {'object_name': 'Quote'},
            'agent': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['skyscanner_scraper.Agent']"}),
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'is_return': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '8', 'decimal_places': '2'}),
            'request_time': ('django.db.models.fields.DateTimeField', [], {})
        },
        u'skyscanner_scraper.station': {
            'Meta': {'object_name': 'Station'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '80', 'primary_key': 'True'}),
            'id': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True', 'db_index': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '80', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['skyscanner_scraper']