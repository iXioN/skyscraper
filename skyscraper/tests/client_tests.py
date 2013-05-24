# -*- coding: utf-8 -*-
#  client_tests.py
#  skyscraper
#  
#  Created by Antonin Lacombe on 2013-05-23.
#  Copyright 2013 Antonin Lacombe. All rights reserved.
# 

import unittest

from skyscraper.tests import fixtures
class ClientTestCase(unittest.TestCase, fixtures.SkyScannerFixture):
    
    def test_get_skyscanner_page(self):
        """
        given any client
        when I get the skyscanner main page
        then I get a status code 200 
        """
        client = self.any_client()
        response  = client.get("/")
        self.assertTrue(response.ok)

    def test_submit_form(self):
        """
        given any informations
        when forge a request with the informations
        then I get 200
        """
        params = {
            "short_from":"NTE",
            "short_to":"EDI",
        }
        response = self.get_any_flights_page(**params)
        self.assertTrue(response.ok)
    
    def test_get_session_key_on_result(self):
        """
        given reponse page of any request
        when I get the session key
        then I have a string with 6 "-"
        """
        client = self.any_client()
        response = self.get_any_flights_page(client)
        session_key = client._get_session_key(response)
    
    def test_get_quotes(self):
        params = {
            "short_from":"NTE",
            "short_to":"EDI",
        }
        quotes = self.get_any_quotes(**params)
        
