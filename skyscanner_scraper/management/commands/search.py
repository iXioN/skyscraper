# -*- coding: utf-8 -*-
#  search.py
#  skyscraper
#  
#  Created by Antonin Lacombe on 2013-05-27.
#  Copyright 2013 Antonin Lacombe. All rights reserved.
# 
import datetime
import math
import time
from optparse import make_option
from django.core.management.base import BaseCommand
from django.db import models
from django.db.models import Q
from django.utils import timezone
from skyscanner_scraper.client import SkyscannerClient
from progressbar import ProgressBar

PRINT_DATE_FORMAT = "%a %d %b %Y"
PRINT_HOUR_FORMAT = "%H:%M"
ARGUMENT_DATE_FORMAT = "%m/%d/%y"

class Command(BaseCommand):
    help = "Search a flight on skyscanner website"   
    option_list = BaseCommand.option_list + (
        make_option(
            '-f',
            '--from',
            # action='store_true',
            dest='from_city',
            metavar='FROM_CITY',
            help='The origin city name',
            type="string",
        ),
        make_option(
            '-t',
            '--to',
            # action='store_true',
            dest='to_city',
            metavar='DESTINATION_CITY',
            help='The city where you want to go',
            type="string",
        ),
        make_option(
            '-d',
            '--depart',
            # action='store_true',
            dest='depart_date',
            metavar='DEPART_DATE',
            help='the date you want to go, format (month/day/year) ex: 05/27/13',
            type="string",
            default=timezone.now().strftime(ARGUMENT_DATE_FORMAT)
        ),
        make_option(
            '-r',
            '--return',
            # action='store_true',
            dest='return_date',
            metavar='RETURN_DATE',
            help='the date you want to return, format (month/day/year) ex: 05/27/13',
            type="string",
            default="",
        ),
        make_option(
            '-l',
            '--limit',
            # action='store_true',
            dest='print_limit',
            metavar='PRINT_LIMIT',
            help='The number of flight o print',
            type="int",
            default=10,
        ),
    )
    
    def handle(self, *args, **options):
        # make sure origin and destination options are present
        if options['from_city'] == None :
            raise CommandError("Option `--from_city=...` must be specified.")
        if options['to_city'] == None :
            raise CommandError("Option `--to_city=...` must be specified.")
        origin_city_name = options['from_city']
        destination_city_name = options['to_city']
        print_limit = options['print_limit']
        depart_date = datetime.datetime.strptime(options['depart_date'], ARGUMENT_DATE_FORMAT).date()
        #if no return date given, the flight is a on way
        return_date = ""
        if options['return_date']:
            return_date = datetime.datetime.strptime(options['return_date'], ARGUMENT_DATE_FORMAT).date()
        
        #instantiate a skyscanner client
        client = SkyscannerClient()
        now = timezone.now()

        origin_station = models.get_model("skyscanner_scraper", "Station").objects.get_or_fetch(origin_city_name)
        destination_station = models.get_model("skyscanner_scraper", "Station").objects.get_or_fetch(destination_city_name)
        
        search_params = {
           "short_from":origin_station.code,
           "short_to":destination_station.code,
           "depart_date":depart_date,
           "return_date":return_date,
        }
        
        #get the result, if no result found at first call, wait and retry (retry max = 6)`
        pricing_option_qs = None
        i = 0
        max_val = 5
        pbar = ProgressBar(maxval=max_val).start()
        while i < max_val:
            i += 1
            query_flight, flights = client.get_flights(**search_params)
            seen_flights_pk  = [f.pk for f in flights]            
            pricing_option_qs = models.get_model('skyscanner_scraper', 'PricingOption').objects.all()            
            #One way flight
            if not query_flight.inbound_date:
                pricing_option_qs = pricing_option_qs.filter(
                   outbound_flight_id__in=seen_flights_pk,
                   inbound_flight__isnull=True,
                   quote__is_return=False,
                )
            #if the query for a return flight, remove the one way flights
            if query_flight.outbound_date and query_flight.inbound_date:
                pricing_option_qs = pricing_option_qs.filter(
                    Q(inbound_flight_id__in=seen_flights_pk) | Q(outbound_flight_id__in=seen_flights_pk),
                    quote__is_return=True
                )
                pricing_option_qs = pricing_option_qs.exclude(
                    Q(inbound_flight__isnull=True) | Q(outbound_flight__isnull=True),
                )
            if len(pricing_option_qs) > 0:
                break
            pbar.update(i)
            time.sleep(1)
        pbar.finish()
        pricing_option_qs = pricing_option_qs.order_by('quote__price')

        #then print the result
        print "---------------------------------------------------------"
        print "search on SkyScanner from %s(%s) to %s(%s)" % (origin_station.name, origin_station.code, destination_station.name, destination_station.code)
        if return_date:
            print "%s - %s" % (depart_date.strftime(PRINT_DATE_FORMAT), return_date.strftime(PRINT_DATE_FORMAT) )
        else:
            print "one way from %s" % (depart_date.strftime(PRINT_DATE_FORMAT))
        print "---------------------------------------------------------"
        
        limit_number = print_limit
        print_count = 0
        #to remove the duplicate flight we will create a key with outbound_flight.pk+inboud_flight.pk
        #if this id is already seen, don't add the price_option
        printed_combination = set()
        for price_option in pricing_option_qs:
            #outbound
            outbound_flight_id = price_option.outbound_flight_id
            #inbound
            inbound_flight_id = price_option.inbound_flight_id
            #printed_combination pk
            combination = "%s_%s" % (outbound_flight_id, inbound_flight_id)
            if not combination in printed_combination:
                self.print_flight_details(price_option)
                #print the informations
                printed_combination.add(combination)
                print_count += 1
                if print_count >= limit_number:
                    break
        print "%s of %s results" % (limit_number, len(pricing_option_qs)) 
        
        #TODO : fix this bug(maybe by adding the query_flight in quote and price_option)
        #delete all quote and pricing_option to avoid complexe mistakes
        models.get_model('skyscanner_scraper', 'Quote').objects.all().delete()
        models.get_model('skyscanner_scraper', 'PricingOption').objects.all().delete()
    
    def print_flight_details(self, price_option):
        """print flight (in and out bound) details"""
        #outbound
        outbound_flight = price_option.outbound_flight
        #inbound
        inbound_flight = price_option.inbound_flight
        rounded_price = math.ceil(price_option.quote.price)
        carrier_list = set(outbound_flight.carrier_set.all().values_list('name', flat=True))
        agent_name = price_option.quote.agent.name
        if inbound_flight:
            carrier_list = carrier_list | set(price_option.inbound_flight.carrier_set.all().values_list('name', flat=True))
        carriers = u" + ".join(carrier_list)
        print u"%i € on %s via %s" % (rounded_price, carriers, agent_name)
        #print the outbound informations
        self.print_flight_detail(outbound_flight, "outbound")
        if inbound_flight:
            #if inboud: print the inbound informations
            self.print_flight_detail(inbound_flight, "inbound")
        print "-------------------------------"
    
    def print_flight_detail(self, flight, way):
        """print a flight detail """
        origin_code = flight.origin_station.code
        destination_code = flight.destination_station.code
        departure_time = flight.departure_time.strftime(PRINT_HOUR_FORMAT)
        arrival_time = flight.arrival_time.strftime(PRINT_HOUR_FORMAT)
        duration = time.strftime('%Hh%M', time.gmtime(flight.duration*60))
        #manage the stop stations
        stop_stations_string = ""
        stop_stations = flight.stop_station_set.all().values_list("code", flat=True)
        if len(stop_stations) > 0:
            stop_station_list = ", ".join(filter(None, stop_stations))
            stop_stations_string = "(%s)" % (stop_station_list)

        print "%s : %s(%s) - %s(%s) stops %s %s %s" % (
            way,
            departure_time, 
            origin_code, 
            arrival_time, 
            destination_code,
            flight.stop_count,
            stop_stations_string,
            duration,
        )
        
