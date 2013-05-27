# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Quote.is_return'
        db.add_column(u'skyscanner_scraper_quote', 'is_return',
                      self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Quote.is_return'
        db.delete_column(u'skyscanner_scraper_quote', 'is_return')


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
            'stop_count': ('django.db.models.fields.IntegerField', [], {'default': '0'})
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