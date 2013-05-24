# 
#  models.py
#  skyscraper
#  
#  Created by Antonin Lacombe on 2013-05-24.
#  Copyright 2013 Antonin Lacombe. All rights reserved.
# 

from django.db import models

class Station(models.Model):
    id = models.IntegerField(primary_key=True)
    code = models.CharField(max_length=80)
    #city = models.ForeignKey("skyscanner_scraper.City")
    name = models.CharField(max_length=80)
    
    def __unicode__(self):
        return u"%s %s" % (self.code, self.name)
        
        
class Quote(models.Model):
    id = models.IntegerField(primary_key=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    request_time = models.DateTimeField()
    
    def __unicode__(self):
        return u"%s %s" % (self.id, self.price)
        
                
class Flight(models.Model):
    id = models.CharField(primary_key=True, max_length=100)
    inbound_itinerary_leg = models.BooleanField(default=True, )
    origin_station = models.ForeignKey('skyscanner_scraper.Station', related_name="origin_flight_set", blank=True, null=True, default=None)
    destination_station = models.ForeignKey('skyscanner_scraper.Station', related_name="destination_flight_set", blank=True, null=True, default=None)
    departure_time = models.DateTimeField(blank=True, default=None, null=True)
    arrival_time = models.DateTimeField(blank=True, default=None, null=True)
    duration = models.IntegerField(default=0)
    stop_count = models.IntegerField(default=0)

    def __unicode__(self):
        return u"%s %s %s" % (self.id, self.origin_station, self.destination_station)


class PricingOption(models.Model):
    quotes_set = models.ManyToManyField('skyscanner_scraper.Quote', blank=True)
    inbound_itinerary_leg = models.ForeignKey('skyscanner_scraper.Flight', related_name="inbound_priceoption_set",)
    outbound_itinerary_leg = models.ForeignKey('skyscanner_scraper.Flight', related_name="outbound_priceoption_set",)
        
    def __unicode__(self):
        return u"%s %s %s " % (self.quotes_set)

