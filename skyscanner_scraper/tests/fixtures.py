# -*- coding: utf-8 -*-
#  fixtures.py
#  skyscraper
#  
#  Created by Antonin Lacombe on 2013-05-24.
#  Copyright 2013 Antonin Lacombe. All rights reserved.
# 
import datetime
from django.utils import timezone
from skyscanner_scraper.client import SkyscannerClient

class SkyScannerFixture(object):
    
    def any_client(self):
        """return a skyscanner client"""
        return SkyscannerClient()
        
    def get_any_flights_page(self, client=None, **kwargs):
        """return a flights page"""
        client = client or SkyscannerClient()
        now = timezone.now()
        params = {
            "short_from":"NTE",
            "short_to":"EDI",
            "depart_date":now,
            "return_date":now + datetime.timedelta(days=5)
        }
        params.update(kwargs)
        return client._get_flights_page(**params)
    
    def get_flights(self, client=None, **kwargs):
        """return some quotes"""
        client = client or SkyscannerClient()
        today = datetime.date.today()
        params = {
            "short_from":"NTE",
            "short_to":"EDI",
            "depart_date":today,
            "return_date":today + datetime.timedelta(days=5)
        }
        params.update(kwargs)
        query_flight, flights = client.get_flights(**params)
        return flights
    
    def get_stations(self, client=None, city_name=""):
        """retur a place instance from a city name using the autosuggest client methode"""
        client = client or SkyscannerClient()
        return client.get_stations(city_name)
        