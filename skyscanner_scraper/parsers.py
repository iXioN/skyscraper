# -*- coding: utf-8 -*-
#  parsers.txt
#  skyscraper
#  
#  Created by Antonin Lacombe on 2013-05-24.
#  Copyright 2013 Antonin Lacombe. All rights reserved.
# 
import datetime
from django.db import models
from skyscanner_scraper.utils import merge_or_create


FEED_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"

class RouteDateParser(object):
    """a route_date parser"""
    def __init__(self, route_date_dict):
        super(RouteDateParser, self).__init__()
        self.route_date_dict = route_date_dict
        
    def handle_stations(self):
        """return stations object seen in feed"""
        stations_set = set()
        Station = models.get_model("skyscanner_scraper", "Station")
        
        station_info_list = self.route_date_dict.get("Stations", {})
        for station_info in station_info_list:
            station_id = station_info["Id"]
            defaults = {
                "name":station_info.get("Name"),
                "code":station_info.get("Code"),
            }
            station, created, merged = merge_or_create(
               Station,
               id = station_id,
               defaults = defaults,
            )
            stations_set.add(station)
        return stations_set
    
    def _get_datetime(self, string_datetime):
        """get a string and return a datetime instance"""
        return datetime.datetime.strptime(string_datetime, FEED_DATETIME_FORMAT)
        
    def handle_quotes(self):
        """return quotes object seen in feed"""
        object_set = set()
        Quote = models.get_model("skyscanner_scraper", "Quote")
        
        quote_info_list = self.route_date_dict.get("Quotes", {})
        for quote_info in quote_info_list:
            quote_id = quote_info["Id"]
            defaults = {
                "price":quote_info.get("Price"),
                "request_time":self._get_datetime(quote_info.get("RequestDateTime")),
            }
            instance, created, merged = merge_or_create(
               Quote,
               id = quote_id,
               defaults = defaults,
            )
            object_set.add(instance)
        return object_set
        
    def handle_flights(self):
        """return flights (inbound and outbound) object seen in feed"""
        object_set = set()
        Flight = models.get_model("skyscanner_scraper", "Flight")
                
        inbound_info_list = self.route_date_dict.get("InboundItineraryLegs", {})
        #add a marker to recognize the inbound and outbound flight after the list merge
        for inbound_itinerary_leg in inbound_info_list:
            inbound_itinerary_leg["is_inbound"] = True
        
        outbound_info_list = self.route_date_dict.get("OutboundItineraryLegs", {})
        #merge the lists
        inbound_info_list.extend(outbound_info_list)
        flights_info_list = inbound_info_list
        for flight_info in flights_info_list:
            flight_id = flight_info["Id"]  
            
            origin_station = models.get_model("skyscanner_scraper", "Station").objects.get_or_create(id=flight_info.get("OriginStation"))[0]
            destination_station = models.get_model("skyscanner_scraper", "Station").objects.get_or_create(id=flight_info.get("DestinationStation"))[0]
            defaults = {
                "origin_station":origin_station,
                "destination_station":destination_station,
                "departure_time":self._get_datetime(flight_info.get("DepartureDateTime")),
                "arrival_time":self._get_datetime(flight_info.get("ArrivalDateTime")),
                "duration":flight_info.get("Duration"),
                "stop_count":flight_info.get("StopsCount"),
                "inbound_itinerary_leg":flight_info.get("is_inbound", False)
            }
            instance, created, merged = merge_or_create(
               Flight,
               id = flight_id,
               defaults = defaults,
            )
            #handle the pricing_options
            self.handle_pricing_options(flight_info.get("PricingOptions", list()), instance)
            
            object_set.add(instance)
        return object_set
    
    def handle_pricing_options(self, pricing_options_info_list, flight):
        """ merge or create the each pricing options """
        PricingOption = models.get_model("skyscanner_scraper", "PricingOption")
        pricing_option_set = set()
        for pricing_option_info in pricing_options_info_list:
            #get the fisrt quote, it's a simplification
            quote_id = pricing_option_info.get("QuoteIds", list())[0]
            quote, created = models.get_model('skyscanner_scraper', 'Quote').objects.get_or_create(id=quote_id)
            #get the opposing flight
            opposing_flight_id = pricing_option_info.get("OpposingLegId")
            opposing_flight = None
            if opposing_flight_id:
                opposing_flight, created = models.get_model('skyscanner_scraper', 'Flight').objects.get_or_create(id=opposing_flight_id)
            
            inbound_flight = None
            outbound_flight = None            
            if flight.inbound_itinerary_leg:
                inbound_flight = flight
                outbound_flight = opposing_flight
            else:
                inbound_flight = opposing_flight
                outbound_flight = flight
                
            instance, created, merged = merge_or_create(
               PricingOption,
               quote = quote,
               inbound_flight=inbound_flight,
               outbound_flight=outbound_flight,
               defaults = {},
            )
            pricing_option_set.add(instance)
        return pricing_option_set
        
    def parse(self):
        """
        parse the routeDate feed from skyscanner,
        return the flight order by their cheapest prices
        """
        #handle stations
        self.handle_stations()
        #handle quotes
        self.handle_quotes()
        #handle flights
        flights = self.handle_flights()
        return flights

        # from django.db.models import Q
        # seen_flights_pk  = [f.pk for f in flights]
        # pricing_option_qs = models.get_model('skyscanner_scraper', 'PricingOption').objects.all()
        # pricing_option_qs = pricing_option_qs.filter(
        #     Q(inbound_flight_id__in=seen_flights_pk) | Q( outbound_flight_id__in=seen_flights_pk)
        # )
        # #for return check the pricing option with inbound and outbound
        # pricing_option_qs = pricing_option_qs.exclude(Q(inbound_flight__isnull=True) | Q(outbound_flight__isnull=True))
        # pricing_option_qs = pricing_option_qs.order_by('quote__price')
