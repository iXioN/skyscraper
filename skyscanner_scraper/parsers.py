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
            }
            instance, created, merged = merge_or_create(
               Flight,
               id = flight_id,
               defaults = defaults,
            )
            object_set.add(instance)
        return object_set
    
        
    def parse(self):
        #handle stations
        self.handle_stations()
        #handle quotes
        self.handle_quotes()
        #handle flights
        flights = self.handle_flights()
        
    #     for json_object_name, object_cache in self.model_mapping.iteritems():
    #         import ipdb
    #         ipdb.set_trace()
    # 
    # def load_models(self):
    #     """load all model"""
    #     for object_name, object_cache in self.objects_mapping.iteritems():
    #         for object_info in self.route_date_dict.get(object_name, {}):
    #             object_id = object_info.get('Id')
    #             if not object_id in object_cache:
    #                 object_cache[object_id] = self.model_mapping[object_name](**object_info)
