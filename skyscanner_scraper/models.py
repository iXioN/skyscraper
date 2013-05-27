# -*- coding: utf-8 -*-
#  models.py
#  skyscraper
#  
#  Created by Antonin Lacombe on 2013-05-24.
#  Copyright 2013 Antonin Lacombe. All rights reserved.
# 

from django.db import models
from skyscanner_scraper.client import SkyscannerClient

class StationManager(models.Manager):
    def get_or_fetch(self, city_name):
        """
        get or fetch a station from a city name
        if multiple stations are found, this function return the first
        """
        #try to get a place on db
        stations = None
        stations = models.get_model("skyscanner_scraper", "Station").objects.filter(name__iexact=city_name)
        if len(stations) == 0:
            #else fetch the results
            client = SkyscannerClient()
            stations = client.get_stations(city_name)
        if len(stations) > 0:
            #return the first
            return stations[0]
         
class Station(models.Model):
    code = models.CharField(max_length=80, primary_key=True)
    id = models.IntegerField(blank=True, null=True, default=None, db_index=True)
    name = models.CharField(blank=True, null=True, default=None, max_length=80)
    objects = StationManager()
    
    def __unicode__(self):
        return u"%s %s" % (self.code, self.name)

class Carrier(models.Model):
    id = models.CharField(max_length=5, primary_key=True)
    name = models.CharField(max_length=80)
    
    def __unicode__(self):
        return u"%s" % (self.name)
        
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
    is_return = models.BooleanField(default=False, db_index=True)
    def __unicode__(self):
        return u"%s € %s" % (self.price, self.agent)


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
    
    carrier_set = models.ManyToManyField('skyscanner_scraper.Carrier')
    query_flight = models.ForeignKey('skyscanner_scraper.QueryFlight')

    def __unicode__(self):
        return u"%s %s %s" % (self.origin_station, self.destination_station, self.carrier_set.all())
