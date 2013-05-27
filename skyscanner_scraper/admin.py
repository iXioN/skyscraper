# 
#  admin.py
#  skyscraper
#  
#  Created by Antonin Lacombe on 2013-05-24.
#  Copyright 2013 Antonin Lacombe. All rights reserved.
# 

from django.contrib import admin
from django.db import models


class StationPriceAdmin(admin.ModelAdmin):
   list_display = ('code', 'name',)
   search_fields = ('name', 'code' )

admin.site.register(models.get_model('skyscanner_scraper', 'Station'), StationPriceAdmin)