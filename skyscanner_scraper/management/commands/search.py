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

PRINT_DATE_FORMAT = "%a %d %b %Y"
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
            default=datetime.datetime.now().strftime(ARGUMENT_DATE_FORMAT)
        ),
        make_option(
            '-r',
            '--return',
            # action='store_true',
            dest='return_date',
            metavar='RETURN_DATE',
            help='the date you want to return, format (month/day/year) ex: 05/27/13',
            type="string",
            default=""#(datetime.datetime.now()+datetime.timedelta(days=7)).strftime(ARGUMENT_DATE_FORMAT)
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
        
        depart_date = datetime.datetime.strptime(options['depart_date'], ARGUMENT_DATE_FORMAT).date()
        
        #if no return date given, the flight must must be a on way
        return_date = ""
        if options['return_date']:
            return_date = datetime.datetime.strptime(options['return_date'], ARGUMENT_DATE_FORMAT).date()
        
        client = SkyscannerClient()
        now = timezone.now()

        origin_station = models.get_model("skyscanner_scraper", "Station").objects.get_or_fetch(origin_city_name)
        destination_station = models.get_model("skyscanner_scraper", "Station").objects.get_or_fetch(destination_city_name)
        
        params = {
           "short_from":origin_station.code,
           "short_to":destination_station.code,
           "depart_date":depart_date,
           "return_date":return_date,
        }
        
        #get the result, if no result found at first call, wait and retry (retry max = 6)`
        pricing_option_qs = None
        i = 0
        while i < 5:
            i += 1
            query_flight, flights = client.get_flights(**params)
            seen_flights_pk  = [f.pk for f in flights]            
        
            pricing_option_qs = models.get_model('skyscanner_scraper', 'PricingOption').objects.all()
            #get all pricing options for the seen flights
            
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
            
            print "retry... %s" % (i)
            time.sleep(2)
        
        pricing_option_qs = pricing_option_qs.order_by('quote__price')

        #then print the result
        print "---------------------------------------------------------"
        print "search on SkyScanner from %s(%s) to %s(%s)" % (origin_station.name, origin_station.code, destination_station.name, destination_station.code)
        if return_date:
            print "%s - %s" % (depart_date.strftime(PRINT_DATE_FORMAT), return_date.strftime(PRINT_DATE_FORMAT) )
        else:
            print "one way from %s" % (depart_date.strftime(PRINT_DATE_FORMAT))
            
        print "---------------------------------------------------------"
        
        seen_flight = set()
        for price_option in pricing_option_qs[:10]:
            print price_option
        
        print "total of %sresults" % (len(pricing_option_qs)) 
        
        #TODO : fix this bug
        #delete all quote and pricing_option to avoid complexe mistakes
        models.get_model('skyscanner_scraper', 'Quote').objects.all().delete()
        models.get_model('skyscanner_scraper', 'PricingOption').objects.all().delete()
        
