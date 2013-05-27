# -*- coding: utf-8 -*-
#  models.py
#  skyscraper
#  
#  Created by Antonin Lacombe on 2013-05-24.
#  Copyright 2013 Antonin Lacombe. All rights reserved.
# 

from django.db import models

class Station(models.Model):
    id = models.IntegerField(primary_key=True)
    code = models.CharField(max_length=80, db_index=True)
    #city = models.ForeignKey("skyscanner_scraper.City")
    name = models.CharField(max_length=80)
    
    def __unicode__(self):
        return u"%s %s" % (self.code, self.name)
      
        
class Agent(models.Model):
    id = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=255)
    default_url = models.URLField(max_length=255)
    booking_number = models.CharField(max_length=80, blank=True, null=True)
    is_carrier = models.BooleanField(default=False)
    
    def __unicode__(self):
        return self.name
        
         
class Quote(models.Model):
    id = models.IntegerField(primary_key=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    request_time = models.DateTimeField()
    agent = models.ForeignKey('skyscanner_scraper.Agent')
    
    def __unicode__(self):
        return u"%s %s €" % (self.id, self.price)


class PricingOption(models.Model):
    quote = models.ForeignKey('skyscanner_scraper.Quote', blank=True)
    inbound_flight = models.ForeignKey('skyscanner_scraper.Flight', related_name="inbound_priceoption_set", blank=True, null=True, default=None)
    outbound_flight = models.ForeignKey('skyscanner_scraper.Flight', related_name="outbound_priceoption_set", blank=True, null=True, default=None)
        
    def __unicode__(self):
        return u"%s %s %s " % (self.quote, self.outbound_flight, self.inbound_flight)


class QueryFlight(models.Model):
    request_id  = models.CharField(max_length=80, primary_key=True)
    outbound_date = models.DateField()
    inbound_date = models.DateField(blank=True, default=None, null=True)
    #cabin_class = models.CharField(max_length=80) 
    origin_station_set = models.ManyToManyField('skyscanner_scraper.Station', related_name="origin_queryflight_set")
    destination_station_set = models.ManyToManyField('skyscanner_scraper.Station', related_name="destination_queryflight_set")
    
    def __unicode__(self):
        origin_stations = ", ".join(self.origin_station_set.all().values_list('code', flat=True))
        destination_stations = ", ".join(self.destination_station_set.all().values_list('code', flat=True))
        return u"%s -> %s from:%s to: %s" % (origin_stations, destination_stations, self.outbound_date, self.inbound_date)


class Flight(models.Model):
    id = models.CharField(primary_key=True, max_length=100)
    inbound_itinerary_leg = models.BooleanField(default=True, db_index=True)
    origin_station = models.ForeignKey('skyscanner_scraper.Station', related_name="origin_flight_set", blank=True, null=True, default=None)
    destination_station = models.ForeignKey('skyscanner_scraper.Station', related_name="destination_flight_set", blank=True, null=True, default=None)
    departure_time = models.DateTimeField(blank=True, default=None, null=True)
    arrival_time = models.DateTimeField(blank=True, default=None, null=True)
    duration = models.IntegerField(default=0)
    stop_count = models.IntegerField(default=0)
    
    query_flight = models.ForeignKey('skyscanner_scraper.QueryFlight')

    def __unicode__(self):
        return u"%s %s %s" % (self.id, self.origin_station, self.destination_station)
