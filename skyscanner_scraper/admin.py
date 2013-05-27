# 
#  admin.py
#  skyscraper
#  
#  Created by Antonin Lacombe on 2013-05-24.
#  Copyright 2013 Antonin Lacombe. All rights reserved.
# 

from django.contrib import admin
from django.db import models


class StationAdmin(admin.ModelAdmin):
   list_display = ('code', 'name',)
   search_fields = ('name', 'code' )
admin.site.register(models.get_model('skyscanner_scraper', 'Station'), StationAdmin)

class CarrierAdmin(admin.ModelAdmin):
   list_display = ('id', 'name',)
   search_fields = ('name', )
admin.site.register(models.get_model('skyscanner_scraper', 'Carrier'), CarrierAdmin)

class AgentPriceAdmin(admin.ModelAdmin):
   list_display = ('name', 'default_url', 'booking_number', 'is_carrier',)
   search_fields = ('name', )
admin.site.register(models.get_model('skyscanner_scraper', 'Agent'), AgentPriceAdmin)