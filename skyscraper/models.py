# -*- coding: utf-8 -*-
#  models.py
#  skyscraper
#  
#  Created by Antonin Lacombe on 2013-05-24.
#  Copyright 2013 Antonin Lacombe. All rights reserved.
# 

class DirectMappingObject(object):
    """ the values given at init are directly set as property"""
    def __init__(self, **kwargs):
        super(DirectMappingObject, self).__init__()
        for k, v in kwargs.iteritems():
            setattr(self, k, v)
        
class Agent(DirectMappingObject):
    """docstring for Agent"""


class Carrier(DirectMappingObject):
    """docstring for Agent"""


class Station(DirectMappingObject):
    """docstring for Station"""

        