# -*- coding: utf-8 -*-
#  parsers.txt
#  skyscraper
#  
#  Created by Antonin Lacombe on 2013-05-24.
#  Copyright 2013 Antonin Lacombe. All rights reserved.
# 

from skyscraper.models import Agent, Carrier, Station

class RouteDateParser(object):
    """a route_date parser"""
    def __init__(self, route_date_dict):
        super(RouteDateParser, self).__init__()
        self.route_date_dict = route_date_dict
        
        self.carriers = {}
        self.agents = {}
        self.stations = {}
        self.objects_mapping = {
            'Carriers':self.carriers,
            'Agents':self.agents,
            'Stations':self.stations,
        }
        #load informations json_name -> Model_class
        self.model_mapping = {
            'Carriers':Carrier,
            'Agents':Agent,
            'Stations':Station,
        }
        self.load_models()
    
    def load_models(self):
        """load all model"""
        for object_name, object_cache in self.objects_mapping.iteritems():
            for object_info in self.route_date_dict.get(object_name, {}):
                object_id = object_info.get('Id')
                if not object_id in object_cache:
                    object_cache[object_id] = self.model_mapping[object_name](**object_info)

    
    def get_quotes(self):
        """return a list of quote objects"""
        import ipdb
        ipdb.set_trace()
        for quote_info in self.route_date_dict.get("Quotes", {}):
            pass