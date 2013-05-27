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
        self.query_flight = None
        
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
    
    def handle_agents(self):
        """return a list of the seen agents"""
        agents_set = set()
        Agent = models.get_model("skyscanner_scraper", "Agent")
        agent_info_list = self.route_date_dict.get("Agents", {})
        for agent_info in agent_info_list:
            agent_id = agent_info["Id"]
            defaults = {
                "name":agent_info.get("Name"),
                "default_url":agent_info.get("DefaultUrl"),
                "booking_number":agent_info.get("BookingNumber"),
                "is_carrier":agent_info.get("IsCarrier"),
            }
            agent, created, merged = merge_or_create(
               Agent,
               id = agent_id,
               defaults = defaults,
            )
            agents_set.add(agent)
        return agents_set
        
    def handle_query_flight(self):
        """return a QueryFlight model object"""
        QueryFlight = models.get_model("skyscanner_scraper", "QueryFlight")
        query_info = self.route_date_dict.get("Query", {})
        
        query_id = query_info['RequestId']

        #get the origin stations, can be multiple if the origin is city with many airport or a country
        origin_stations_id = query_info["OriginPlaceInfo"].get("AirportIds", list())
        origin_stations_qs = models.get_model("skyscanner_scraper", "Station").objects.all().filter(code__in=origin_stations_id)
        #get the destination stations,
        destination_stations_id = query_info["DestinationPlaceInfo"].get("AirportIds", list())
        destination_stations_qs = models.get_model("skyscanner_scraper", "Station").objects.all().filter(code__in=destination_stations_id)
        
        defaults = {
            "inbound_date":self._get_datetime(query_info.get("InboundDate")).date(),
            "outbound_date":self._get_datetime(query_info.get("OutboundDate")).date(),
        }
        query_flight, created, merged = merge_or_create(
           QueryFlight,
           request_id = query_id,
           defaults = defaults,
        )
        query_flight.origin_station_set = origin_stations_qs
        query_flight.destination_station_set = destination_stations_qs        
        self.query_flight = query_flight
        return query_flight
    
    def _get_agent(self, quote_request_id):
        """return an agent instance from a quote_request_id"""
        if not hasattr(self, '_quote_request_agent_cache'):
            self._quote_request_agent_cache = dict()
            #create a dict with quote_request_id is the key and the value is the agent
            for quote_request_info in self.route_date_dict.get("QuoteRequests", list()):
                quote_request_id = quote_request_info.get("Id")
                agent_id = quote_request_info.get("AgentId")
                agent, created = models.get_model("skyscanner_scraper", "Agent").objects.get_or_create(id=agent_id)
                self._quote_request_agent_cache[quote_request_id] = agent
        return self._quote_request_agent_cache[quote_request_id]
             
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
                "agent":self._get_agent(quote_info.get("QuoteRequestId"))
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
                "inbound_itinerary_leg":flight_info.get("is_inbound", False),
                "query_flight":self.query_flight,
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
                opposing_flight, created = models.get_model('skyscanner_scraper', 'Flight').objects.get_or_create(
                    id=opposing_flight_id,
                    query_flight_id=self.query_flight.request_id,
                )
            
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
        #handle agents
        self.handle_agents()
        #handle the query
        self.handle_query_flight()
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
